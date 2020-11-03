import click
import numpy as np
import pandas as pd
from sklearn import model_selection
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from mlxtend.classifier import StackingClassifier
from sklearn.neighbors import KNeighborsClassifier

import warnings
warnings.simplefilter('ignore')


def get_data(df, train=True):
    """Converts data in dataframe to numpy array comprised of one-hot vectors"""
    # Encode all categorical variables
    encoder = OneHotEncoder()
    encoder.fit(df[['age', 'gender', 'hispanic', 'race_ethnicity', 'state']])

    # Get target variable if train set and data matrix
    if train:
        y = df['vote_2020'].values.astype(float)
        X = encoder.transform(
            df[['age', 'gender', 'hispanic', 'race_ethnicity', 'state']]).toarray()
        return (X, y)
    else:
        return encoder.transform(df[['age', 'gender', 'hispanic', 'race_ethnicity', 'state']]).toarray()


def fit_model(X, y, n_jobs=1):
    """Fits the Stacking model

    Warning: This function takes aprox. 25 min to run
    """
    # Classifiers
    clf1 = KNeighborsClassifier(n_neighbors=1)
    clf2 = RandomForestClassifier(random_state=1)
    clf3 = SVC()
    lr = LogisticRegression()
    stack = StackingClassifier(classifiers=[clf1, clf2, clf3],
                               meta_classifier=lr)

    # Parameters to tune and optimize
    params = {'kneighborsclassifier__n_neighbors': [1, 5],
              'randomforestclassifier__n_estimators': [10, 50],
              'meta_classifier__C': [0.1, 10.0]}

    # We perform grid search for cross validation
    grid = model_selection.GridSearchCV(estimator=stack,
                                        param_grid=params,
                                        cv=5,
                                        refit=True,
                                        n_jobs=n_jobs,
                                        verbose=1)

    # Fit to training data
    grid.fit(X, y)  # Approx 25 min. to fit
    display_metrics(grid)

    return grid


def display_metrics(grid):
    """To add verbosity for the model"""
    cv_keys = ('mean_test_score', 'std_test_score', 'params')

    for r, _ in enumerate(grid.cv_results_['mean_test_score']):
        print("%0.3f +/- %0.2f %r" % (grid.cv_results_[cv_keys[0]][r],
                                      grid.cv_results_[cv_keys[1]][r],
                                      grid.cv_results_[cv_keys[2]][r]))

        print('Best parameters: %s' % grid.best_params_)
        print('Accuracy: %.2f' % grid.best_score_)


def get_post_strat_table(df):
    """Creates poststratification cells as a table"""
    table = pd.pivot_table(df, values='perwt', index=['age', 'gender', 'hispanic', 'race_ethnicity', 'state'],
                           dropna=True, aggfunc=np.sum)

    flattened = pd.DataFrame(table.to_records())
    N = np.sum(flattened['perwt'])

    flattened['prop'] = flattened['perwt'] / N

    return flattened


def srp_forecast(table, predictions):
    """Poststratify estimates and return final predictions"""
    table['predictions'] = predictions
    table['predictions_prop'] = table['predictions'] * table['prop']

    N = np.sum(table['perwt'])
    p = table.groupby('state')['predictions_prop'].sum() * N
    w = table.groupby('state')['perwt'].sum()

    return p / w


@click.command()
@click.option('--n-workers', default=1, help="Number of concurrent processes to use for training the model")
@click.option('--train', required=True, help='Relative or full path to training data')
@click.option('--post', required=True, help='Relative or full path to poststratifying data')
def main(n_workers, train, post):
    """Given training data and poststratification data this script
    fits the SRP Model and outputs poststratified predictions.

    WARNING: This script may more than 30 min to finish.
    """

    # Gather training data and convert to one-hot matrix
    traind = pd.read_csv(train)
    X, y = get_data(traind, train=True)

    # Train model
    model = fit_model(X, y, n_jobs=n_workers)

    # Output model metrics
    display_metrics(model)

    # Gather Poststratification data
    post = pd.read_csv(post)

    # Cells for poststratification
    table = get_post_strat_table(post)

    # Get one-hot matrix to pass into model
    X_pred = get_data(post, train=False)

    # Generate base estimates
    predictions = model.predict(X_pred)

    # Generate poststratified predictions
    forecast = srp_forecast(table, predictions)

    # Save to csv file
    forecast.to_csv('spr_forecast.csv')


if __name__ == "__main__":
    main()
