import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

df = pd.read_csv("data/sales.csv")
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

models = [
    ("Linear regression", LinearRegression()),
    ("Random forest", RandomForestRegressor(n_estimators=200, random_state=42)),
]

for name, model in models:
    model.fit(X_train, y_train)
    score = r2_score(y_test, model.predict(X_test))
    print(f"{name}: test R2 = {score:.3f}")