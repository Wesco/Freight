"""
Created on May 5, 2014

@author: TReische
"""

from config import *
import reports
from pandas import read_excel
from fnmatch import fnmatch
from os import listdir, path, remove
from datetime import datetime
import pandas as pd
import numpy as np
import re
import smtp
import xlrd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', help='Location of the config file')
parser.add_argument('-i', '--input', help='Input file')
parser.add_argument('-o', '--output', help='Output file')
args = parser.parse_args()

if args.config is None:
    conf = Config()
else:
    conf = Config(args.config)


def get_reference(df):
    branch = conf.branch

    data = str(df)
    result = None

    if type(df) == bytes:
        data = str(data, 'cp1250', 'ignore')

    if type(data) == str:
        result = re.search(r'%s(-)?\d{6}' % branch, data)

    if result is not None:
        result = result.group(0).replace("-", "").replace("3615", "")

    return result


def is_incoming(df):
    find = conf.incoming_search
    string = str(df, 'cp1250', 'ignore').lower()
    return any([s in string for s in find])


if __name__ == "__main__":
    # Read every UPS file in the watch folder
    for name in listdir(conf.watch_dir):
        if fnmatch(name, '*.xls'):
            wkbk = xlrd.open_workbook(path.join(conf.watch_dir, name),
                                      ragged_rows=True)
            sheet1 = wkbk.sheet_by_name("Sheet1")
            ups_dt_tuple = xlrd.xldate_as_tuple(sheet1.cell_value(3, 2), 0)[0:3]
            ups_date = datetime(ups_dt_tuple[0], ups_dt_tuple[1], ups_dt_tuple[2])

            ups_df = read_excel(io=wkbk,
                                sheetname='Sheet2',
                                header=1,
                                skip_footer=1,
                                engine='xlrd')

            poi_df = reports.poi(conf.open_poi_dir, conf.hist_poi_dir)
            oor_df = reports.customers(conf.oor_dir, conf.branch)
            sup_df = reports.suppliers(conf.gaps_dir, conf.branch)
            sm_df = reports.sales_margin(conf.sm_dir, 6)

            # Look for reference numbers in Reference and Destination Columns
            ups_df['REF'] = ups_df['Reference'].apply(get_reference)
            ups_df['REF'].update(ups_df['Destination'].apply(get_reference))

            # Match REF numbers to PO Numbers
            poi_df = poi_df[poi_df[' PO NUMBER'].isin([x for x in ups_df['REF']])]
            poi_df.set_index(' PO NUMBER', inplace=True)
            ups_df = pd.DataFrame.join(ups_df, poi_df, on='REF', how='left')

            # Get a list of reference numbers that could not be matched to POs
            unmatched = []
            for x, y in zip(ups_df['REF'], ups_df['ORDER']):
                if not pd.isnull(x) and pd.isnull(y):
                    unmatched.append(x)

            # Convert the list to a DataFrame and drop duplicates
            if unmatched:
                unmatched_df = pd.DataFrame(data=unmatched,
                                            columns=['ORDER NO'])
                unmatched_df.drop_duplicates(inplace=True)
                unmatched_df.set_index(unmatched_df['ORDER NO'], inplace=True)

                # If a reference number was not a PO it is assumed to be an
                # order and is merged back into the DataFrame in the 'ORDER'
                # column
                ups_df['ORDER'].update(
                    ups_df.join(unmatched_df, on='REF', how='left')['ORDER NO']
                    )

            # Merge OOR data and UPS data on order numbers
            ups_df = ups_df.join(oor_df, on='ORDER', how='left')

            # Remove from 'ORDERS' column if a customer could not be found
            for i in range(0, len(ups_df['ORDER'])):
                if pd.isnull(ups_df['CUSTOMER'][i]) \
                        and ups_df['ORDER'][i] != '0':
                    ups_df['ORDER'][i] = None

            # UPS Stock Sheet
            ups_stock = ups_df[ups_df['ORDER'] == '0']

            # UPS Incoming Sheet
            ups_incoming = ups_df[(ups_df['Destination'].apply(is_incoming)) & (ups_df['ORDER'] != '0')]

            # UPS Outgoing Sheet
            ups_outgoing = ups_df[ups_df['Destination'].apply(lambda dest: not is_incoming(dest))]

            # Merge suppliers onto sales and margin
            sm_df = sm_df.join(sup_df, on='sim', how='left')
            sm_df.dropna(inplace=True)
            sm_df.rename(columns={'Supplier_no': 'supplier_no'}, inplace=True)
            sm_df['supplier_no'] = sm_df['supplier_no'].apply(str.upper)

            # Calculate total sales for each supplier
            sup_totals = pd.DataFrame(pd.pivot_table(data=sm_df,
                                                     values='cost',
                                                     index='supplier_no',
                                                     aggfunc=np.sum))

            # Calculate total sales per dpc for each supplier
            sm_df = pd.DataFrame(pd.pivot_table(data=sm_df,
                                                values='cost',
                                                index=['supplier_no', 'dpc'],
                                                aggfunc=np.sum))

            # Divide dpc sales by supplier sales
            sm_df['percent'] = sm_df['cost'] / sup_totals['cost']

            # Remove cost totals since they are no longer needed
            del sm_df['cost']

            # Reset index to supplier number
            sm_df.reset_index(level=1, inplace=True)

            # Sum by supplier
            stock_piv = pd.DataFrame(pd.pivot_table(data=ups_stock,
                                                    values='Billed Charges',
                                                    index='SUPPLIER',
                                                    aggfunc=np.sum))

            # Merge Sales and Margin
            stock_piv = stock_piv.join(sm_df, how='left')

            # Calculate the amount each DPC has to pay
            stock_piv['total'] = stock_piv['Billed Charges'] * stock_piv['percent']

            stock_piv['SUPPLIER'] = stock_piv.index

            dpc_totals = pd.DataFrame(pd.pivot_table(data=stock_piv,
                                                     values='total',
                                                     index='dpc',
                                                     aggfunc=np.sum))

            ups_stock_billing = dpc_totals[dpc_totals['total'] > 10]
            ups_stock_billing.reset_index(level=0, inplace=True)

            ups_stock_not_billed = dpc_totals[dpc_totals['total'] < 10]
            ups_stock_not_billed.reset_index(level=0, inplace=True)

            # Write to excel
            i = 0
            filename = '%s %s-%s-%s UPS.xlsx' % ((conf.branch,) + ups_dt_tuple)
            while path.isfile(path.join(conf.output_dir, filename)):
                i += 1
                filename = '%s %s-%s-%s UPS (%s).xlsx' % ((conf.branch,) + ups_dt_tuple + (i,))

            writer = pd.ExcelWriter(path.join(conf.output_dir, filename))

            ups_df.to_excel(writer, 'UPS', index=False)
            ups_incoming.to_excel(writer, 'INCOMING', index=False)
            ups_outgoing.to_excel(writer, 'OUTGOING', index=False)

            ups_stock_billing.to_excel(writer, 'STOCK BILLING', index=False)
            ups_stock_not_billed.to_excel(writer, 'STOCK NOT BILLED', index=False)
            ups_stock.to_excel(writer, 'STOCK', index=False)
            stock_piv.to_excel(writer, 'STOCK BREAKDOWN', index=False)

            writer.sheets['INCOMING'].set_tab_color('green')
            writer.sheets['OUTGOING'].set_tab_color('green')
            writer.sheets['STOCK BILLING'].set_tab_color('green')

            writer.save()
            remove(path.join(conf.watch_dir, name))

            if conf.send_email:
                emailer = smtp.Smtp("email.wescodist.com")
                emailer.connect()
                emailer.send(To=conf.send_to,
                             From=conf.send_from,
                             Subject=filename,
                             Body="",
                             files=[path.join(conf.output_dir, filename)])
                emailer.disconnect()

            if not conf.write_to_disk:
                remove(path.join(conf.output_dir, filename))
