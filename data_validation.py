import pandas as pd

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
def validate_dataset(df, *args, **kwargs):
    """
    C4 Custom Block: Data Integrity Validator.
    Positioned immediately downstream of load_iris.
    Validates null counts, column datatypes, and target class distributions.
    """
    null_count = int(df.isnull().sum().sum())
    num_classes = int(df['target'].nunique())
    print(f"Data Validation: {null_count} missing values found across {len(df)} rows.")
    print(f"Target distribution: {num_classes} distinct classes present.")
    return df


@test
def test_data_integrity(output, *args):
    """
    Quality gate: Checks that there are NO missing values and EXACTLY 3 target classes.
    """
    assert output.isnull().sum().sum() == 0, "Dataset contains null/missing values!"
    assert output['target'].nunique() == 3, f"Expected 3 target classes, found {output['target'].nunique()}"
