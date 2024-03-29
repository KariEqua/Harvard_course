import csv
import sys
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """

    df_evidence = pd.read_csv('shopping.csv')
    series_labels = df_evidence.pop('Revenue')

    bool_mapping = {True: 1, False: 0}
    visitor_mapping = {'Returning_Visitor': 1, 'New_Visitor': 0}
    month_mapping = {'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'June': 5, 'Jul': 6, 'Aug': 7,
                     'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11}

    # should be 1 if the user visited on a weekend and 0 otherwise
    df_evidence['Weekend'] = df_evidence['Weekend'].map(bool_mapping)

    # should be 1 for returning visitors and 0 for non-returning visitors
    # for 'other' values: -1, change type to int
    df_evidence['VisitorType'] = df_evidence['VisitorType'].map(visitor_mapping).fillna(-1)
    df_evidence['VisitorType'] = df_evidence['VisitorType'].astype(int)

    # should be 0 for January, 1 for February, 2 for March, etc. up to 11 for December
    df_evidence['Month'] = df_evidence['Month'].map(month_mapping)

    # should either be the integer 1, if the user did go through with a purchase, or 0 otherwise
    series_labels = series_labels.map(bool_mapping)

    evidences = df_evidence.values.tolist()
    labels = series_labels.tolist()

    return evidences, labels


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)

    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    true_positive = 0
    false_negative = 0
    true_negative = 0
    false_positive = 0

    for label, predict in zip(labels, predictions):
        if predict == 1:
            if label == 1:
                true_positive += 1
            else:
                false_positive += 1
        else:
            if label == 1:
                false_negative += 1
            else:
                true_negative += 1

    sensitivity = true_positive / (true_positive + false_negative)
    specificity = true_negative / (true_negative + false_positive)

    return sensitivity, specificity


if __name__ == "__main__":
    main()
