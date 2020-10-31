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
    """TODO: Add description"""
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
    """TODO: Add description

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
    """TODO: Add description"""
    cv_keys = ('mean_test_score', 'std_test_score', 'params')

    for r, _ in enumerate(grid.cv_results_['mean_test_score']):
        print("%0.3f +/- %0.2f %r" % (grid.cv_results_[cv_keys[0]][r],
                                      grid.cv_results_[cv_keys[1]][r],
                                      grid.cv_results_[cv_keys[2]][r]))

        print('Best parameters: %s' % grid.best_params_)
        print('Accuracy: %.2f' % grid.best_score_)


def get_post_strat_table(df):
    """TODO: Add description"""
    table = pd.pivot_table(df, values='perwt', index=['age', 'gender', 'hispanic', 'race_ethnicity', 'state'],
                           dropna=True, aggfunc=np.sum)

    flattened = pd.DataFrame(table.to_records())
    N = np.sum(flattened['perwt'])

    flattened['prop'] = flattened['perwt'] / N

    return flattened


def srp_forecast(table):
    """TODO: Add description"""
    pass


@ click.command()
def main():
    """TODO: Add description"""
    pass


if __name__ == "__main__":
    main()
