from mage_ai.data_preparation.decorators import transformer, test
import pandas as pd

@transformer
def transform(df, *args, **kwargs):
    df["split"] = "train"
    df.loc[120:, "split"] = "test"
    return df

@test
def test_split_is_80_20(output, *args):
    assert (output["split"] == "train").sum() == 120
    assert (output["split"] == "test").sum() == 30
