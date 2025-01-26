import enum


class Emotion(enum.Enum):
    joy = ("joy", "радость")
    sadness = ("sadness", "грусть")
    anger = ("anger", "гнев")
    anxiety = ("anxiety", "тревога")
    shame = ("shame", "стыд")
    disappointment = ("disappointment", "разочарование")
    hope = ("hope", "надежда")
    neutral = ("neutral", "нейтральное")
    unknown = ("unknown", "неизвестное")

    def __init__(self, string, ru_string):
        self.string = string
        self.ru_string = ru_string

    @staticmethod
    def from_russian_name(ru_string):
        for emotion in Emotion:
            if ru_string == emotion.ru_string:
                return emotion

        return Emotion.unknown

    @staticmethod
    def from_name(string):
        for emotion in Emotion:
            if string == emotion.string:
                return emotion

        return Emotion.unknown
