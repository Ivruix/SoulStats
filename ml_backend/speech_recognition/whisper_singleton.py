import threading
# import whisper


class WhisperRecognizer:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.model = whisper.load_model("base")
        self.lock = threading.Lock()

    def transcribe(self, audio_path):
        with self.lock:
            result = self.model.transcribe(audio_path)
        return result["text"]
