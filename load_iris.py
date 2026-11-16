import pandas as pd
from sklearn.datasets import load_iris

# Import Mage's decorators only if they aren't already loaded in the runtime environment
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader if 'mage_ai' in globals() else lambda f: f
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test if 'mage_ai' in globals() else lambda f: f


@data_loader
def load_data(*args, **kwargs):
    """
    Step 1: Load the built-in Iris dataset from scikit-learn as a pandas DataFrame.
    Returns:
        pd.DataFrame: 150 rows containing 4 feature columns + 'target'.
    """
    iris = load_iris(as_frame=True)
    df = iris.frame  # 4 feature columns + 'target'
    print(f"Loaded Iris dataset with {len(df)} rows and {df.shape[1]} columns.")
    return df


@test
def test_output(output, *args):
    """
    Quality gate: Verify that the dataset has exactly 150 records.
    If the count differs, execution halts immediately.
    """
    assert len(output) == 150, f"Expected 150 rows in Iris dataset, but received {len(output)}"
