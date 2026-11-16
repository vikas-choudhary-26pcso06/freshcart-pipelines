import pandas as pd
from sklearn.model_selection import train_test_split

# Import Mage's decorators only if they aren't already loaded
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
def transform(df, *args, **kwargs):
    """
    Step 2: Prepare and partition dataset.
    Splits the 150-row DataFrame into an 80/20 train/test split (120 train, 30 test)
    and labels each row with a 'split' column.
    """
    test_size = float(kwargs.get('test_size', 0.2))
    train_df, test_df = train_test_split(df, test_size=test_size, random_state=42)

    train_df = train_df.copy()
    test_df = test_df.copy()
    train_df['split'] = 'train'
    test_df['split'] = 'test'

    result = pd.concat([train_df, test_df], ignore_index=True)
    print(f"Prepared data: {len(train_df)} train rows | {len(test_df)} test rows")
    return result


@test
def test_output(output, *args):
    """
    Quality gate: Verify that the 'split' column exists and contains valid partition labels.
    """
    assert 'split' in output.columns, "Output DataFrame is missing the required 'split' column"
    assert (output['split'] == 'train').sum() > 0, "Train partition cannot be empty"
    assert (output['split'] == 'test').sum() > 0, "Test partition cannot be empty"
