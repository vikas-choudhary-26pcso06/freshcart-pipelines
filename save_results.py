import pandas as pd
import os

@data_exporter
def export_data(data, *args, **kwargs):
    os.makedirs("export", exist_ok=True)
    data.to_csv("export/iris_predictions.csv", index=False)
