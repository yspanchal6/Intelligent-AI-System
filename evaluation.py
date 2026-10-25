
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_score,
)
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

from intents import examples


def evaluate_model():
    texts = [text for text, intent in examples]
    labels = [intent for text, intent in examples]

    # 1. Create a reproducible train/test split.
    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.25,
        random_state=42,
        stratify=labels,
    )

    # 2. Create the ML model.
    model = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2)),
        LogisticRegression(max_iter=1000, random_state=42),
    )

    # 3. Evaluate using stratified 5-fold cross-validation.
    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    cv_scores = cross_val_score(
        model,
        texts,
        labels,
        cv=cv,
        scoring="accuracy",
    )

    print("\n=== 5-FOLD CROSS-VALIDATION ===")
    print(
        "Fold accuracies:",
        [round(score * 100, 2) for score in cv_scores],
    )
    print(f"Mean accuracy: {cv_scores.mean():.2%}")
    print(f"Standard deviation: {cv_scores.std():.2%}")

    # 4. Train on the training set and evaluate on the held-out test set.
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    # 5. Compare with a simple baseline.
    baseline = DummyClassifier(strategy="most_frequent")
    baseline.fit(X_train, y_train)
    baseline_predictions = baseline.predict(X_test)

    print("\n=== BASELINE COMPARISON ===")
    print(
        f"Baseline accuracy: "
        f"{accuracy_score(y_test, baseline_predictions):.2%}"
    )
    print(
        f"ML model accuracy: "
        f"{accuracy_score(y_test, predictions):.2%}"
    )

    # 6. Show misclassified test examples.
    print("\n=== MISCLASSIFIED TEST EXAMPLES ===")

    for text, actual, predicted in zip(X_test, y_test, predictions):
        if actual != predicted:
            print(f"Text: {text!r}")
            print(f"Actual intent: {actual}")
            print(f"Predicted intent: {predicted}")
            print("-" * 40)

    # 7. Print detailed evaluation metrics.
    print("\n=== MODEL EVALUATION ===")
    print(f"Test examples: {len(y_test)}")
    print(f"Accuracy: {accuracy_score(y_test, predictions):.2%}")

    print("\n=== CLASSIFICATION REPORT ===")
    print(classification_report(y_test, predictions, zero_division=0))

    print("=== CONFUSION MATRIX ===")
    print("Intent labels:", model.classes_)
    print(
        confusion_matrix(
            y_test,
            predictions,
            labels=model.classes_,
        )
    )


if __name__ == "__main__":
    evaluate_model()
