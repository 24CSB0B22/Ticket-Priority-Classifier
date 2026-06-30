import streamlit as st
import joblib
import re
import nltk

nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="IT Ticket Priority Classifier",
    page_icon="🎫",
    layout="centered"
)

# -----------------------------
# Load Model
# -----------------------------
@st.cache_resource
def load_model():
    model = joblib.load("models/model.pkl")
    vectorizer = joblib.load("models/vectorizer.pkl")
    return model, vectorizer

# -----------------------------
# Text Cleaning
# -----------------------------
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-z\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    words = [
        lemmatizer.lemmatize(word)
        for word in text.split()
        if word not in stop_words and len(word) > 2
    ]

    return " ".join(words)

# -----------------------------
# Prediction
# -----------------------------
def predict(ticket):

    cleaned = clean_text(ticket)
    vector = vectorizer.transform([cleaned])
    prediction = model.predict(vector)[0]

    confidence = None

    if hasattr(model, "predict_proba"):
        confidence = model.predict_proba(vector).max() * 100

    return prediction, confidence


# -----------------------------
# Load Model
# -----------------------------
try:
    model, vectorizer = load_model()
    model_loaded = True
except:
    model_loaded = False

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Project Info")

st.sidebar.info(
"""
Model : Logistic Regression / Linear SVM

Dataset : 600 Tickets

Vectorizer : TF-IDF

Framework : Streamlit
"""
)

# -----------------------------
# Main Page
# -----------------------------
st.title("🎫 IT Support Ticket Priority Classifier")

st.write(
"Enter an IT support ticket below. The trained machine learning model predicts its priority."
)

ticket = st.text_area(
    "Ticket Description",
    height=150,
    placeholder="Example: Server crashed and all employees cannot access their files."
)

if st.button("Predict Priority", use_container_width=True):

    if not model_loaded:
        st.error("Model not found.")
    elif ticket.strip() == "":
        st.warning("Please enter a ticket.")
    else:

        pred, conf = predict(ticket)

        if pred == "High":
            st.error(f"🔴 HIGH PRIORITY")

        elif pred == "Medium":
            st.warning(f"🟡 MEDIUM PRIORITY")

        else:
            st.success(f"🟢 LOW PRIORITY")

        if conf is not None:
            st.write(f"**Confidence:** {conf:.2f}%")

# -----------------------------
# Sample Tickets
# -----------------------------
st.divider()

st.subheader("Sample Tickets")

samples = [

    "Server crashed and customer data is inaccessible.",

    "Printer on floor 2 is not working.",

    "Need Microsoft Excel installed.",

    "Forgot my email password.",

    "Entire office network is down."

]

for sample in samples:

    if st.button(sample):

        pred, conf = predict(sample)

        st.write("**Ticket**")

        st.info(sample)

        st.write("**Prediction**")

        st.success(pred)

        if conf is not None:
            st.write(f"Confidence : {conf:.2f}%")

st.divider()

st.caption(
"Built using Python • Scikit-Learn • Streamlit • NLTK"
)