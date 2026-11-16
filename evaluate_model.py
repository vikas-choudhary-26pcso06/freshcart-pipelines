from mage_ai.data_preparation.decorators import transformer, test

@transformer
def transform(data, *args, **kwargs):
    return data
