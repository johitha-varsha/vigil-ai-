from flask import Flask, render_template, request, redirect, session, jsonify
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
import random

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- USER STORAGE ----------------
users = {}

# ---------------- ML MODEL ----------------
data = pd.DataFrame({
    "time": ["day","night","night","day"],
    "area": ["crowded","isolated","crowded","isolated"],
    "movement": ["walking","running","walking","running"],
    "light": ["bright","dark","dark","bright"],
    "risk": ["low","high","medium","medium"]
})

encoders = {}
for col in data.columns:
    le = LabelEncoder()
    data[col] = le.fit_transform(data[col])
    encoders[col] = le

X = data[["time","area","movement","light"]]
y = data["risk"]

model = DecisionTreeClassifier()
model.fit(X, y)

# ---------------- AUTH ----------------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if u in users and users[u] == p:
            session["user"] = u
            return redirect("/dashboard")

    return render_template("login.html")


@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        users[u] = p
        return redirect("/")
    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("index.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# ---------------- AI ----------------
@app.route("/predict", methods=["POST"])
def predict():
    data_input = request.json
    df = pd.DataFrame([data_input])

    for col in df.columns:
        df[col] = encoders[col].transform(df[col])

    pred = model.predict(df)[0]
    risk = encoders["risk"].inverse_transform([pred])[0]

    return jsonify({"risk": risk})

# ---------------- MONITOR ----------------
@app.route("/monitor")
def monitor():
    return render_template("monitor.html")

@app.route("/live_risk")
def live_risk():
    return jsonify({"risk": random.choice(["low","medium","high"])})

# ---------------- EMERGENCY ----------------
@app.route("/emergency")
def emergency():
    return render_template("emergency.html")

@app.route("/sos")
def sos():
    return jsonify({"msg": "🚨 SOS SENT!"})

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)