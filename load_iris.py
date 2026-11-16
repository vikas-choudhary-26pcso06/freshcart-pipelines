from sklearn.datasets import load_iris
import pandas as pd

@data_loader
def load_data(*args, **kwargs):
    return load_iris(as_frame=True).frame
