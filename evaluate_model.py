import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

if 'transformer' not in globals():
    try:
        from mage_ai.data_preparation.decorators import transformer
    except ImportError:
        def transformer(f):
            return f
if 'test' not in globals():
    try:
        from mage_ai.data_preparation.decorators import test
    except ImportError:
        def test(f):
            return f


@transformer
def evaluate(df, *args, **kwargs):
    """
    Step 4b (Evaluation Branch):
    Computes confusion matrix and macro classification metrics (accuracy, precision, recall, F1).
    """
    y_true = df['target']
    y_pred = df['predicted']

    cm = pd.crosstab(y_true, y_pred, rownames=['Actual'], colnames=['Predicted'])
    print("Confusion Matrix:")
    print(cm)

    metrics = pd.DataFrame({
        'metric': ['accuracy', 'precision', 'recall', 'f1_score'],
        'value': [
            round(accuracy_score(y_true, y_pred), 3),
            round(precision_score(y_true, y_pred, average='macro'), 3),
            round(recall_score(y_true, y_pred, average='macro'), 3),
            round(f1_score(y_true, y_pred, average='macro'), 3),
        ]
    })
    print("\nModel Evaluation Metrics:")
    print(metrics)
    return metrics


@test
def test_evaluation_metrics(output, *args):
    """
    Quality gate: Verify metrics table structure and that F1 score is positive.
    """
    assert len(output) == 4, "Metrics table must contain 4 evaluation metrics"
    f1_val = output.loc[output['metric'] == 'f1_score', 'value'].values[0]
    assert f1_val >= 0.70, f"Macro F1-score {f1_val} is unacceptably low"
