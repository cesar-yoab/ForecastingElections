import os
import click
import pandas as pd

# Some copy warnings for the pandas data frame
import warnings
warnings.filterwarnings('ignore')

# https://gist.github.com/rogerallen/1583593
US_STATE_CODES = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}


def get_keys():
    """Using the txt keys files returns a list with the codes for the wanted columns"""
    lines = list()

    with open('./util/post_strat_keys.txt', 'r') as f:
        running_str = ""
        for line in f:
            if line == '\n':
                lines.append(running_str.strip())
                running_str = ""
                continue
            running_str += line

        lines.append(running_str)
    return lines


def clean_col(df, col, vals):
    """Remap code to var definition"""
    vals_replace = {}

    for i, line in enumerate(vals.split('\n')):
        if i == 0:
            continue
        v = line.split('		')
        vals_replace[int(v[0])] = v[1]

    df[col].replace(vals_replace, inplace=True)


def finish_clean(df):
    """Finish clean and return as a new data frame"""
    # First replace state names with state codes
    df['STATEICP'].replace(US_STATE_CODES, inplace=True)

    # Binning of race
    race = {
        'Black/African American/Negro': 'Black, or African American',
        'Other Asian or Pacific Islander': 'Pacific',
        'Japanese': 'Asian',
        'Chinese': 'Asian',
        'Other race, nec': 'Some other race',
        'Two major races': 'Some other race',
        'Three or more major races': 'Some other race'
    }

    df['RACE'].replace(race, inplace=True)

    # Binarize hispanic
    hisp = set(df['HISPAN'])

    hisp_rmp = {f: 'Hispanic' for f in hisp if f != 'Not Hispanic'}
    df['HISPAN'].replace(hisp_rmp, inplace=True)

    # Filtering age
    filter = (df['AGE'] >= 18) & (df['AGE'] <= 93)

    df = df[filter]

    # Create age groups
    age_groups = [18, 30, 40, 50, 60, 70, 80, 93]
    age_labs = ['18-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-93']

    df['AGE'] = pd.cut(df['AGE'], age_groups, labels=age_labs)

    return df.dropna()


@click.command()
@click.option('--data', help='Relative or full path for the ipsum data set')
@click.option('--csv-name', default='post-strat.csv', help='Name for the csv file to be created')
def main(data, csv_name):
    """Cleaning script for the IPUMS data set.

        WARNING: This data set should follow the selection guidelines
            outlined in the README. Unexpected behaviour is to be expected
            if they are not followed.
    """
    post_strat = pd.read_csv(data)

    # Only select wanted columns
    cols = ['PERWT', 'SEX', 'AGE', 'RACE', 'HISPAN', 'STATEICP']
    post_strat = post_strat[cols]

    # Get code values from .txt file and clean columns
    lines = get_keys()

    to_clean = ['STATEICP', 'SEX', 'RACE', 'HISPAN']

    for i, col in enumerate(to_clean):
        clean_col(post_strat, col, lines[i])

    # Apply binning as in the survey data set
    post_strat = finish_clean(post_strat)

    # Rename columns
    col_names = {
        'SEX': 'gender',
        'AGE': 'age',
        'RACE': 'race_ethnicity',
        'HISPAN': 'hispanic',
        'STATEICP': 'state',
        'PERWT': 'perwt'
    }
    post_strat = post_strat.rename(col_names, axis='columns')

    # Save as a csv file
    post_strat.to_csv('post-strat.csv')


if __name__ == "__main__":
    main()
