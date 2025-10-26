import openai
import base64
import os

BOSON_API_KEY = "bai-WGJ83y5ZQ_guFFtPSDu0OWJ11AwRN4p_1zKQ5SKlt3BBsmBz"

def encode_audio_to_base64(file_path: str) -> str: 
    """Encode audio file to base64 format."""
    with open(file_path, "rb") as audio_file:
        return base64.b64encode(audio_file.read()).decode("utf-8")

client = openai.Client(
    api_key=BOSON_API_KEY,
    base_url="https://hackathon.boson.ai/v1"
)

# Transcribe audio
audio_path = "/Users/pranav/Downloads/beachKSNA1-Twr-126800-Oct-24-2025-0430Z.mp3"
audio_base64 = encode_audio_to_base64(audio_path)
file_format = audio_path.split(".")[-1]

# Chat about the audio
#audio_path = "/path/to/your/audio.wav"
audio_base64 = encode_audio_to_base64(audio_path)
file_format = audio_path.split(".")[-1]

response = client.chat.completions.create(
    model="higgs-audio-understanding-Hackathon",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": [
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": audio_base64,
                        "format": file_format,
                    },
                },
            ],
        },
        {
            "role": "user",
            "content": "print the audio word for word",
        },
    ],
    max_completion_tokens=256,
    temperature=0.0,
)

print(response.choices[0].message.content)