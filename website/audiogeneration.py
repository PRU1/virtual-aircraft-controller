"""
Replaced proprietary/Boson TTS with an open-source model.

The original implementation (using an API key and remote model) has been commented out below
for reference. We now use the Silero TTS model (open-source) via PyTorch Hub to synthesize
speech locally and save it to output.wav.

Dependencies (install into your venv):
  - torch
  - numpy

This runs fully locally (no API calls). On first run, PyTorch Hub will download the model.
"""

# --- Original code (commented out) ---
# from openai import OpenAI
# import base64
# import os
#
# BOSON_API_KEY = "..."
# client = OpenAI(api_key=BOSON_API_KEY, base_url="https://hackathon.boson.ai/v1")
#
# def b64(path):
#     return base64.b64encode(open(path, "rb").read()).decode("utf-8")
#
# def generateAudio(inputText):
#     ...
#     open("output.wav", "wb").write(base64.b64decode(audio_b64))

import os
import numpy as np
import torch
import wave


def _write_wav_mono(path: str, samples: np.ndarray, sample_rate: int) -> None:
    """Write a mono 16-bit PCM WAV file from float32 samples [-1, 1]."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    # Clamp and convert to int16
    pcm16 = np.clip(samples, -1.0, 1.0)
    pcm16 = (pcm16 * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(48000)
        wf.writeframes(pcm16.tobytes())


def generateAudio(text: str, out_path: str = "output.wav", speaker: str = "en_57", sample_rate: int = 48000) -> str:
    """
    Generate speech audio from text using Silero TTS (open-source) and save to out_path.

    Params:
      - text: Text to synthesize
      - out_path: Output WAV file path (default: output.wav)
      - speaker: One of Silero English speakers (e.g., en_0..en_116)
      - sample_rate: Target sample rate (default: 48000)

    Returns:
      - The path to the generated WAV file
    """
    # Select device
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Load Silero TTS model (English pack v3)
    # Docs: https://github.com/snakers4/silero-models
    model, example_text = torch.hub.load(
        repo_or_dir="snakers4/silero-models",
        model="silero_tts",
        language="en",
        speaker="v3_en",
        trust_repo=True,
    )
    model.to(device)

    # Synthesize speech (returns a Torch tensor on CPU)
    audio: torch.Tensor = model.apply_tts(
        text=text,
        speaker=speaker,
        sample_rate=sample_rate,
    )

    # Ensure on CPU and convert to numpy float32
    if audio.is_cuda:
        audio = audio.cpu()
    samples = audio.numpy().astype(np.float32)

    # Write to WAV (mono, 16-bit PCM)
    _write_wav_mono(out_path, samples, sample_rate)
    return out_path


if __name__ == "__main__":
    generateAudio("Hello, this is a local open-source TTS test.")