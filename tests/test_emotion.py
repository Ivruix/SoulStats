import unittest
from ml_backend.data_types.emotion import Emotion


class TestEmotion(unittest.TestCase):
    def test_emotion_string(self):
        self.assertEqual(Emotion.joy.string, "joy")
        self.assertEqual(Emotion.sadness.string, "sadness")
        self.assertEqual(Emotion.anger.string, "anger")
        self.assertEqual(Emotion.anxiety.string, "anxiety")
        self.assertEqual(Emotion.disappointment.string, "disappointment")
        self.assertEqual(Emotion.hope.string, "hope")
        self.assertEqual(Emotion.surprise.string, "surprise")
        self.assertEqual(Emotion.neutral.string, "neutral")
        self.assertEqual(Emotion.unknown.string, "unknown")

    def test_emotion_ru_string(self):
        self.assertEqual(Emotion.joy.ru_string, "радость")
        self.assertEqual(Emotion.sadness.ru_string, "грусть")
        self.assertEqual(Emotion.anger.ru_string, "гнев")
        self.assertEqual(Emotion.anxiety.ru_string, "тревога")
        self.assertEqual(Emotion.disappointment.ru_string, "разочарование")
        self.assertEqual(Emotion.hope.ru_string, "надежда")
        self.assertEqual(Emotion.surprise.ru_string, "удивление")
        self.assertEqual(Emotion.neutral.ru_string, "нейтральное")
        self.assertEqual(Emotion.unknown.ru_string, "неизвестное")

    def test_from_russian_name(self):
        self.assertEqual(Emotion.from_russian_name("радость"), Emotion.joy)
        self.assertEqual(Emotion.from_russian_name("грусть"), Emotion.sadness)
        self.assertEqual(Emotion.from_russian_name("гнев"), Emotion.anger)
        self.assertEqual(Emotion.from_russian_name("тревога"), Emotion.anxiety)
        self.assertEqual(Emotion.from_russian_name("разочарование"), Emotion.disappointment)
        self.assertEqual(Emotion.from_russian_name("надежда"), Emotion.hope)
        self.assertEqual(Emotion.from_russian_name("удивление"), Emotion.surprise)
        self.assertEqual(Emotion.from_russian_name("нейтральное"), Emotion.neutral)
        self.assertEqual(Emotion.from_russian_name("неизвестное"), Emotion.unknown)

    def test_from_name(self):
        self.assertEqual(Emotion.from_name("joy"), Emotion.joy)
        self.assertEqual(Emotion.from_name("sadness"), Emotion.sadness)
        self.assertEqual(Emotion.from_name("anger"), Emotion.anger)
        self.assertEqual(Emotion.from_name("anxiety"), Emotion.anxiety)
        self.assertEqual(Emotion.from_name("disappointment"), Emotion.disappointment)
        self.assertEqual(Emotion.from_name("hope"), Emotion.hope)
        self.assertEqual(Emotion.from_name("surprise"), Emotion.surprise)
        self.assertEqual(Emotion.from_name("neutral"), Emotion.neutral)
        self.assertEqual(Emotion.from_name("unknown"), Emotion.unknown)


if __name__ == '__main__':
    unittest.main()
