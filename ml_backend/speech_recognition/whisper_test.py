import whisper

model = whisper.load_model("base")
result = model.transcribe(r"test.mp3")

print(result["text"])

# TODO: Use with threading.Lock
