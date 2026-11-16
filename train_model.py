from mage_ai.data_preparation.decorators import transformer, test

@transformer
def transform(df, *args, **kwargs):
    return df

@test
def test_accuracy(output, *args):
    assert True
