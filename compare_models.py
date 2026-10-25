
from sklearn.model_selection import (
    StratifiedKFold,
    cross_val_score,
    train_test_split,
)
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import make_pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from intents import examples


def compare_models():
    texts = [text for text, intent in examples]
    labels = [intent for text, intent in examples]

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    # Model A: Current word-level TF-IDF model.
    model_a = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2)),
        LogisticRegression(max_iter=1000, random_state=42),
    )

    # Model B: Combine word-level and character-level TF-IDF.
    model_b = make_pipeline(
        FeatureUnion([
            (
                "word",
                TfidfVectorizer(
                    analyzer="word",
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                ),
            ),
            (
                "char",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(2, 5),
                    min_df=1,
                    sublinear_tf=True,
                ),
            ),
        ]),
        LogisticRegression(max_iter=1000, random_state=42),
    )

    models = {
        "Model A - Word TF-IDF": model_a,
        "Model B - Word + Character TF-IDF": model_b,
    }

    
    # Create one fixed held-out test set.
    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.25,
        random_state=42,
        stratify=labels,
    )

    for name, model in models.items():
        # Cross-validation on the complete dataset.
        scores = cross_val_score(
            model,
            texts,
            labels,
            cv=cv,
            scoring="accuracy",
        )

        # Train only on the training portion and evaluate on held-out data.
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        test_accuracy = accuracy_score(y_test, predictions)

        print(f"\n=== {name} ===")
        print("CV fold accuracies:", [round(s * 100, 2) for s in scores])
        print(f"CV mean accuracy: {scores.mean():.2%}")
        print(f"CV standard deviation: {scores.std():.2%}")
        print(f"Held-out test accuracy: {test_accuracy:.2%}")

        print("\nClassification report:")
        print(
            classification_report(
                y_test,
                predictions,
                zero_division=0,
            )
        )

        


if __name__ == "__main__":
    compare_models()
