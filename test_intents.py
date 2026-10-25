
"""Smoke tests for the intent dataset and classifier."""

import unittest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from intents import examples


class TestIntentDataset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        texts = [text for text, _ in examples]
        labels = [label for _, label in examples]

        cls.model = make_pipeline(
            TfidfVectorizer(),
            LogisticRegression(max_iter=1000, random_state=42),
        )
        cls.model.fit(texts, labels)

    def test_dataset_has_multiple_intents(self):
        self.assertGreaterEqual(len(examples), 50)
        self.assertGreaterEqual(len({label for _, label in examples}), 5)

    def test_basic_classifier_fit_and_predict(self):
        self.assertEqual(self.model.predict(["hello"])[0], "greeting")

    def test_technical_questions(self):
        questions = [
            "what is recursion",
            "explain recursion",
            "explain the osi model",
            "what is a stack in data structures",
            "explain computer networks",
            "what is an operating system",
        ]

        for question in questions:
            with self.subTest(question=question):
                self.assertEqual(
                    self.model.predict([question])[0],
                    "ask_gemini",
                )


if __name__ == "__main__":
    unittest.main()
