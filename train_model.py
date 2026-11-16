import joblib
from sklearn.tree import DecisionTreeClassifier

# Import Mage decorators safely for both Mage runtime and pure Python execution
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

# The 4 measurement columns used to predict species
FEATURES = ['sepal length (cm)', 'sepal width (cm)',
            'petal length (cm)', 'petal width (cm)']


@transformer
def train(df, *args, **kwargs):
    """
    Step 3: Train Decision Tree Classifier.
    Reads max_depth from runtime variables, fits on train split,
    predicts on test split, logs accuracy, serializes model, and returns test DataFrame.
    """
    max_depth = int(kwargs.get('max_depth', 3))

    train_df = df[df['split'] == 'train']
    test_df = df[df['split'] == 'test'].copy()

    model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    model.fit(train_df[FEATURES], train_df['target'])

    test_df['predicted'] = model.predict(test_df[FEATURES])
    accuracy = (test_df['predicted'] == test_df['target']).mean()
    print(f"Trained DecisionTree(max_depth={max_depth}) | Test accuracy: {accuracy:.4f}")

    joblib.dump(model, 'iris_model.pkl')
    return test_df


@test
def test_accuracy(output, *args):
    """
    Quality gate: Ensures model accuracy meets production standards (>= 80%).
    If accuracy drops below 80%, this assertion fails, aborting all downstream blocks.
    """
    accuracy = (output['predicted'] == output['target']).mean()
    assert accuracy >= 0.80, f"Model accuracy {accuracy:.4f} is below the 80% threshold!"
