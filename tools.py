import json
import os

import matplotlib
matplotlib.use("Agg")  # save charts to files without opening windows
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

DATA_PATH = "data/sales.csv"
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the data once when the program starts
df = pd.read_csv(DATA_PATH)
df["date"] = pd.to_datetime(df["date"])
df["month"] = df["date"].dt.strftime("%Y-%m")


def describe_dataset():
    """Return row count, column types, valid text values, and the first 5 rows."""
    info = {
        "rows": len(df),
        "columns": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "text_column_values": {
            col: sorted(df[col].unique().tolist())
            for col in ["region", "product"]
        },
        "preview": df.head().to_string(),
    }
    return json.dumps(info, indent=2)


def run_pandas(code):
    """Run pandas code written by the model. The answer must be stored in a variable called result."""
    namespace = {"df": df.copy(), "pd": pd}
    try:
        exec(code, namespace)
    except Exception as e:
        return f"Error while running the code: {e}. Fix the code and try again."
    if "result" not in namespace:
        return "Error: the code must store the answer in a variable called result."
    return str(namespace["result"])


def make_chart(group_by, value, chart_type, title, filename):
    """Sum a numeric column for each group and save a bar or line chart as a PNG."""
    if group_by not in df.columns or value not in df.columns:
        return f"Error: columns must come from {list(df.columns)}"
    if chart_type not in ("bar", "line"):
        return "Error: chart_type must be 'bar' or 'line'."

    summary = df.groupby(group_by)[value].sum()
    if chart_type == "bar":
        summary = summary.sort_values(ascending=False)
    else:
        summary = summary.sort_index()

    fig, ax = plt.subplots(figsize=(8, 5))
    if chart_type == "bar":
        summary.plot(kind="bar", ax=ax)
    else:
        summary.plot(kind="line", marker="o", ax=ax)

    ax.set_title(title)
    ax.set_ylabel(value)
    fig.tight_layout()

    path = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(path)
    plt.close(fig)
    return f"Chart saved to {path}"

def train_revenue_model():
    """Train a linear regression that predicts revenue_aed and report its R2 score on rows it did not train on."""
    features = pd.get_dummies(
        df[["quantity", "discount", "product"]],
        columns=["product"],
        drop_first=True,
        dtype=float,
    )
    target = df["revenue_aed"]

    X_train, X_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42
    )
    model = LinearRegression().fit(X_train, y_train)
    score = r2_score(y_test, model.predict(X_test))

    return f"Linear regression trained on quantity, discount, and product. Test R2: {score:.3f}"