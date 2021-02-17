# https://labor.ny.gov/app/warn/default.asp

import requests
# from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd

import warnings
# warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')


def generate_case_IDs(year=2020):

    status_done = False

    while not status_done:
        try:
            year_page = f'https://labor.ny.gov/app/warn/default.asp?warnYr={year}'
            page = requests.post(year_page)
            soup = BeautifulSoup(page.content, 'html.parser',
                                 from_encoding=page.encoding.lower())
            table_content = soup.find("table")
            all_links = table_content.find_all('a', href=True)

            ID_list = []
            for link in all_links:
                item = link['href'].split('details.asp?id=')[1]
                ID_list.append(item)

            status_done = True

        except Exception as error:
            #print(f'Error occurred. MessageL {error}')
            continue

    return ID_list


def generate_dataset(case_IDs):

    key_list = ['Company', 'Business Type',  'County', 'Total Employees', 'Number Affected',
                'Date of Notice', 'Layoff Date', 'Closing Date',
                'Reason for Dislocation', 'Classification', 'Reason Stated for Filing', 'Union',
                'Contact', 'Phone', 'FEIN NUM', 'Event Number']

    WARN_df = pd.DataFrame()

    for case in case_IDs:
        case_done = False
        while not case_done:
            try:
                case_url = f'https://labor.ny.gov/app/warn/details.asp?id={case}'
                page = requests.post(case_url)
                # from_encoding="iso-8859-1')
                soup = BeautifulSoup(
                    page.content, 'html.parser', from_encoding=page.encoding.lower())
                table_content = soup.find("table")
                all_lines = table_content.find_all('p')
                list1 = [ele.get_text().strip().replace(u'\xa0', u'')
                         for ele in all_lines if len(ele.get_text().strip()) > 0]
                # dict1 = dict(s.split(':', maxsplit = 1) for s in list1 if s.split(':', maxsplit = 1)[0] in key_list)

                list2 = [s.split(':', maxsplit=1) for s in list1 if s.split(
                    ':', maxsplit=1)[0] in key_list]

                list3 = []
                for b in list2:
                    # for unintended error: dictionary update sequence element has length of 1, 2 is required
                    if len(b) == 2:
                        list3.append([item.strip() for item in b])

                dict1 = dict(s for s in list3)

                dict1["Case_ID"] = case
                WARN_df = WARN_df.append(dict1, ignore_index=True)

                case_done = True

                # Print Progress
                done_pct = case_IDs.index(case) / len(case_IDs)
                print(f'{done_pct * 100:.2f}% done', end='\r', flush=True)

            except Exception as error:
                # print(f'Error occurred. MessageL {error}')
                continue

    col_order = [item for item in key_list if item in list(
        WARN_df.columns)] + ["Case_ID"]

    WARN_df = WARN_df[col_order].sort_values(by=["Case_ID"], ascending=False)
    return WARN_df


if __name__ == "__main__":

    # years = [item for item in range(2001, 2021)]
    years = [2021]

    for year in years:
        print(f'Doing Year {year}')
        case_list = generate_case_IDs(year=year)
        df = generate_dataset(case_IDs=case_list)
        file_name = f'data/{year}.csv'
        df.to_csv(file_name, index=False)

    ####################
    # Save List as File
    ####################
    # with open('listfile.txt', 'w') as filehandle:
    #     for listitem in list1:
    #         filehandle.write('%s\n' % listitem)
