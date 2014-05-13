'''
Created on May 5, 2014

@author: TReische
'''

from config import Config
import reports
from pandas import read_excel
from fnmatch import fnmatch
from os import listdir, path, remove
import pandas as pd
import re
from smtp import smtp
from getpass import getuser

conf = Config()


def get_reference(df):
    branch = conf.branch
    result = re.search(branch + r"(-)?\d{6}", str(df))
    if result is not None:
        return int(result.group(0).replace("-", "").replace("3615", ""))


def is_incoming(df):
    find = conf.incoming_search
    string = str(df).lower()
    return any([s in string for s in find])


if __name__ == '__main__':
    poi = reports.Poi(conf.open_poi_dir, conf.hist_poi_dir)
    oor = reports.Oor(conf.oor_dir)

    # Read every UPS file in the watch folder
    for name in listdir(conf.watch_dir):
        if fnmatch(name, '*.xls'):
            upsdf = read_excel(io=path.join(conf.watch_dir, name),
                               sheetname='Sheet2',
                               header=1,
                               skip_footer=1)

            # Look for reference numbers in Reference and Destination Columns
            upsdf['REF'] = upsdf['Reference'].apply(get_reference)
            upsdf['REF'].update(upsdf['Destination'].apply(get_reference))

            # Match REF numbers to PO Numbers
            poi = poi[poi[' PO NUMBER'].isin([x for x in upsdf['REF']])]
            poi.set_index(' PO NUMBER', inplace=True)
            upsdf = pd.DataFrame.join(upsdf, poi, on='REF', how='left')
            # Get a list of reference numbers that could not be matched to POs
            unmatched = []
            for x, y in zip(upsdf['REF'], upsdf['ORDER']):
                if not pd.isnull(x) and pd.isnull(y):
                    unmatched.append(x)

            # Convert the list to a DataFrame and drop duplicates
            unmatched_df = pd.DataFrame(data=unmatched, columns=['ORDER NO'])
            unmatched_df.drop_duplicates(inplace=True)
            unmatched_df.set_index(unmatched_df['ORDER NO'], inplace=True)

            # If a reference number was not a PO it is assumed to be an order
            # and is merged back into the DataFrame in the 'ORDER' column
            upsdf['ORDER'].update(
                upsdf.join(unmatched_df, on='REF', how='left')['ORDER NO']
                )

            # Merge OOR data and UPS data on order numbers
            upsdf = upsdf.join(oor, on='ORDER', how='left')

            # Remove from 'ORDERS' column if a customer could not be found
            for i in range(0, len(upsdf['ORDER'])):
                if pd.isnull(upsdf['CUSTOMER'][i]) and upsdf['ORDER'][i] != 0:
                    upsdf['ORDER'][i] = None

            ups_stock = upsdf[upsdf['ORDER'] == 0]
            ups_incoming = upsdf[(upsdf['Destination'].apply(is_incoming)) &
                                 (upsdf['ORDER'] != 0)]
            ups_outgoing = \
                upsdf[upsdf['Destination'].apply(is_incoming) == False]

            # Write to excel
            filename = 'temp\\%s UPS.xlsx' % conf.branch
            writer = pd.ExcelWriter(filename)

            upsdf.to_excel(writer, 'UPS', index=False)
            ups_stock.to_excel(writer, 'STOCK', index=False)
            ups_incoming.to_excel(writer, 'INCOMING', index=False)
            ups_outgoing.to_excel(writer, 'OUTGOING', index=False)

            writer.save()

            mail = smtp("email.wescodist.com")
            mail.connect()
            mail.send(getuser() + "@wesco.com",
                      conf.email,
                      "UPS",
                      "Test email :D",
                      [filename])
            mail.disconnect()

            remove(filename)
