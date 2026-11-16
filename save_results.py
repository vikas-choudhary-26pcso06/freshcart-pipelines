# Import Mage decorator safely
if 'data_exporter' not in globals():
    try:
        from mage_ai.data_preparation.decorators import data_exporter
    except ImportError:
        def data_exporter(f):
            return f


@data_exporter
def export_data(df, *args, **kwargs):
    """
    Step 4a: Export test predictions to CSV file.
    Only executes if the upstream train_model block and its @test quality gate pass.
    """
    output_path = kwargs.get('output_path', 'iris_predictions.csv')
    df.to_csv(output_path, index=False)
    print(f"Successfully saved {len(df)} predictions to {output_path}")
