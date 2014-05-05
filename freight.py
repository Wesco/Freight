'''
Created on May 5, 2014

@author: TReische
'''

from config import Config
import reports
from pandas import read_excel
from fnmatch import fnmatch
from os import listdir, path
import pandas as pd
import re


def get_reference(df):
    result = re.search(r"3615(-)?\d{6}", str(df))
    if result is not None:
        return int(result.group(0).replace("-", "").replace("3615", ""))


if __name__ == '__main__':
    conf = Config()
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
            upsdf = upsdf.join(poi, on='REF', how='left')

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

            # Write the result to a file
            upsdf.to_csv('bin\\upsdf.csv')
