from mage_ai.data_preparation.decorators import transformer, test

@transformer
def transform(df, *args, **kwargs):
    return df.dropna().reset_index(drop=True)

@test
def test_schema_integrity(output, *args):
    assert output.isna().sum().sum() == 0, "Null values detected"
    assert output["target"].nunique() == 3, "Expected 3 target species"
