import openai
import base64
import os

BOSON_API_KEY = "bai-Osa4rXyZAhT2bCT94vvm_oxytprX5_WgqFbcU1E3ZLj2rxKN"

def encode_audio_to_base64(file_path: str) -> str:
    """Encode audio file to base64 format."""
    with open(file_path, "rb") as audio_file:
        return base64.b64encode(audio_file.read()).decode("utf-8")

client = openai.Client(
    api_key=BOSON_API_KEY,
    base_url="https://hackathon.boson.ai/v1"
)

# Transcribe audio
audio_path = "E:/bosonai/KLAX-Tower-North-133.9-GND-Jul-12-2025-2130Z SWA1110 vs UAL348 NOT_REALTIME.mp3"



def transcribe_audio(audio_path):
    audio_base64 = encode_audio_to_base64(audio_path)
    file_format = audio_path.split(".")[-1]
    response = client.chat.completions.create(
        model="higgs-audio-understanding-Hackathon",
        messages=[
            {"role": "system", "content": "Transcribe the recording."},
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
        ],
        max_completion_tokens=256,
        temperature=0.2,
    )
    print("TRANSCRIPTION RESULTTTTTTTT")
    print(response.choices[0].message.content)

    return response.choices[0].message.content

