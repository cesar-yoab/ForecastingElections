import zipfile
import click
import pandas as pd
from os import getcwd, path, walk


FEATURES_OF_INTEREST = ['age', 'gender', 'hispanic',
                        'race_ethnicity', 'state', 'education']


def clean_downloaded_data(dirpath, csvname):
    """Unzips and cleans data"""
    # Create data frame
    df = create_df(dirpath)

    if isinstance(df, dict):
        print("An unexpected error ocurred please re-check your input and data!")
        return

    # Clean data
    df = _raw_clean_data(df)

    # Write csv file
    df.to_csv(csvname)


def get_path_to_phase2(dirpath):
    """Returns full path to phase 2 study directory."""
    if not 'Nationscape-DataRelease_WeeklyMaterials_DTA' in dirpath:
        PATH = path.join(
            dirpath, 'Nationscape-DataRelease_WeeklyMaterials_DTA')
    else:
        PATH = dirpath

    dirs = [f[0] for f in walk(dirpath)]
    # Refer to function list_files

    for f in dirs:
        name = f.split('/')[-1]
        if "phase_2" in name:
            return path.join(PATH, name)

    return PATH


def create_df(dirpath):
    """Returns a data frame with loaded data from .dta files.

    Args:
        dirpath: Path to directory containing zip file,
            this directory will be used to store the 
            csv file during the conversion process

    Returns:
        Pandas data frame
    """
    PATH = get_path_to_phase2(dirpath)

    dirs = [f[0] for f in walk(PATH)][1::]
    concat_df = None

    for f in dirs:  # Iterate over directories
        dirname = f.split('/')[-1]  # f has the form /some/path/to/dir

        # We look for the June surveys
        if not 'ns202006' in dirname:
            continue

        # Loads the STATA file into a dataframe
        df = pd.read_stata(path.join(PATH, dirname, dirname+".dta"))

        try:
            # Read stata file and concat to dataframe
            if concat_df is None:
                concat_df = select_features(df)
                continue

            # Merges data frames, we can call this function because
            # Columns represent the same thing
            concat_df = pd.concat(
                [concat_df, select_features(df)], ignore_index=True)

        # For debuggin purposes, we may remove this later
        except Exception:
            print("Error with {} file".format(dirname + '.dta'))

    return concat_df if concat_df is not None else {}


def select_features(df):
    """Selects features of interest from dataframe."""
    if 'vote_2020' not in df.columns:
        df.rename(columns={'vote_2020_v1': 'vote_2020'}, inplace=True)

    return df[FEATURES_OF_INTEREST + ['vote_2020']]


def extract_data(filepath, dirpath):
    """Unzip downloaded data.

    Args:
        filepath: Downloaded zip file path 
    """
    if not path.exists(filepath):  # Sanity check
        print("{} does not exist!\nCheck that you are using the correct path." % filepath)
        return

    with zipfile.ZipFile(filepath, 'r') as zipf:
        zipf.extractall(dirpath)


def _raw_clean_data(survey):
    """Remaps values and cleans the data for saving"""

    # Remap values for vote choice 2016 and 2020
    remp_2020 = {
        'I am not sure/don\'t know': 'No Vote',
        'I will not vote, but am eligible': 'No Vote',
        'I would not vote': 'No Vote',
        'I am not eligible to vote': 'No Vote'
    }
    survey['vote_2020'].replace(remp_2020, inplace=True)

    # From this point on we represent a Biden vote as a 1 and a trump vote as a 0
    survey.replace({'Joe Biden': 1, 'Donald Trump': 0}, inplace=True)

    # Create age groups
    age_groups = [18, 30, 40, 50, 60, 70, 80, 93]
    age_labs = ['18-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-93']

    survey['age'] = pd.cut(survey['age'], age_groups, labels=age_labs)

    # Replace Hispanic values for hispanic or not
    rmp = {k: 'Hispanic' for k in set(
        survey['hispanic']) if k != 'Not Hispanic'}

    survey['hispanic'].replace(rmp, inplace=True)

    # Replacing race keys
    race_keys = set(survey['race_ethnicity'])

    race_rmp = {k: 'Asian' for k in race_keys if 'Asian' in k}

    race_rmp = {**race_rmp, **
                {k: 'Pacific' for k in race_keys if 'Pacific' in k}}

    survey['race_ethnicity'].replace(race_rmp, inplace=True)

    # We only really care about Joe Biden/Donald Trump votes
    return survey.loc[(survey['vote_2020'] == 0) | (survey['vote_2020'] == 1)]


@click.command()
@click.option('--unzip/--no-unzip', default=False)
@click.option('--csv-name', default='survey-data.csv')
@click.option('--data', help='Relative or full path of folder containing data')
def main(unzip, csv_name, data):
    """Script to clean and in unzip data after download"""
    if unzip:
        extract_data(data, './data')

    clean_downloaded_data(data, csv_name)


if __name__ == '__main__':
    main()
