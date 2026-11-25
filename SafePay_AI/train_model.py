"""Training pipeline for SafePay AI's Scikit-learn LogisticRegression threat detector.

Note: This prototype trains on fictional, synthetic multilingual training data
(English, Hindi, and Kannada). Its predictions are probabilistic indicators of
possible coercion/suspicion and are NOT guaranteed to detect every threat or
language.
"""

import os
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "transaction_dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "trained_model.pkl")

NUMERIC_FEATURE_COLUMNS = [
    "transaction_amount",
    "average_amount",
    "amount_deviation_ratio",
    "new_receiver_indicator",
    "unusual_transaction_time",
    "customer_transaction_count",
    "user_reported_pressure",
    "remote_guidance_indicator",
    "receiver_verified",
    "feels_safe",
]


def build_feature_matrix(
    df: pd.DataFrame,
    vectorizer: TfidfVectorizer,
    scaler: StandardScaler,
    fit: bool = False,
):
    """Combine character-level TF-IDF text features with scaled numeric features."""
    texts = df["text"].fillna("").astype(str)
    numeric_values = df[NUMERIC_FEATURE_COLUMNS].astype(float).to_numpy()

    if fit:
        text_features = vectorizer.fit_transform(texts)
        scaled_numeric = scaler.fit_transform(numeric_values)
    else:
        text_features = vectorizer.transform(texts)
        scaled_numeric = scaler.transform(numeric_values)

    return hstack([text_features, csr_matrix(scaled_numeric)]).tocsr()


def train_and_save_model(
    dataset_path: str = DATASET_PATH,
    model_path: str = MODEL_PATH,
) -> Tuple[Dict[str, object], str]:
    """Train LogisticRegression on synthetic multilingual data and save artifact."""
    df = pd.read_csv(dataset_path)
    X_train_df, X_test_df, y_train, y_test = train_test_split(
        df,
        df["label"].astype(int),
        test_size=0.25,
        random_state=42,
        stratify=df["label"].astype(int),
    )

    # Character-level n-grams recognize patterns across English, Hindi, and Kannada
    # (including Devanagari, Kannada script, and romanized spellings).
    vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=2,
        sublinear_tf=True,
    )
    scaler = StandardScaler()

    X_train = build_feature_matrix(X_train_df, vectorizer, scaler, fit=True)
    X_test = build_feature_matrix(X_test_df, vectorizer, scaler, fit=False)

    classifier = LogisticRegression(
        max_iter=1000,
        C=1.5,
        class_weight="balanced",
        random_state=42,
    )
    classifier.fit(X_train, y_train)

    y_pred = classifier.predict(X_test)
    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "train_samples": int(len(X_train_df)),
        "test_samples": int(len(X_test_df)),
    }

    artifact = {
        "classifier": classifier,
        "vectorizer": vectorizer,
        "scaler": scaler,
        "numeric_columns": NUMERIC_FEATURE_COLUMNS,
        "metrics": metrics,
        "prototype_disclaimer": (
            "Prototype trained on synthetic multilingual data (English, Hindi, Kannada). "
            "Predictions are not guaranteed to detect every threat or language."
        ),
    }
    joblib.dump(artifact, model_path)
    return metrics, model_path


if __name__ == "__main__":
    eval_metrics, saved_path = train_and_save_model()
    print("=== SafePay AI Scikit-learn LogisticRegression Training ===")
    print(f"Saved model artifact: {saved_path}")
    print(f"Train samples: {eval_metrics['train_samples']} | Test samples: {eval_metrics['test_samples']}")
    print(f"Accuracy : {eval_metrics['accuracy']:.4f}")
    print(f"Precision: {eval_metrics['precision']:.4f}")
    print(f"Recall   : {eval_metrics['recall']:.4f}")
    print(f"F1-score : {eval_metrics['f1_score']:.4f}")
    print(f"Confusion Matrix: {eval_metrics['confusion_matrix']}")
