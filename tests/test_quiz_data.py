import json
import unittest
from pathlib import Path


QUIZ_PATH = Path(__file__).parents[1] / "data" / "quiz_data.json"


class QuizDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.questions = json.loads(QUIZ_PATH.read_text(encoding="utf-8"))

    def test_exactly_twenty_unique_questions(self):
        self.assertEqual(len(self.questions), 20)
        self.assertEqual(len({q["id"] for q in self.questions}), 20)

    def test_every_answer_is_an_option(self):
        for question in self.questions:
            with self.subTest(question=question["id"]):
                self.assertIn(question["answer"], question["options"])
                self.assertEqual(len(question["options"]), 4)
                self.assertEqual(len(set(question["options"])), 4)

    def test_required_content_is_present(self):
        required = {"difficulty", "types", "question", "options", "answer", "explanation"}
        for question in self.questions:
            self.assertTrue(required.issubset(question))


if __name__ == "__main__":
    unittest.main()
