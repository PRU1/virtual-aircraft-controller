# openai sample code for audio transcription
# modified for boson ai hackathon
# used openai because I couldn't get transcription to work with boson's models -- (was limited to one line outputs and I couldn't figure out why)

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset


def generate_transcription(audio_file_path: str):

    """ generate transcription given an audio file. 

    Args:
        audio_file_path (str): path to audio file

    Returns:
        str: transcribed string
    """

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-large-v3-turbo"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        chunk_length_s=30,
        batch_size=16,  # batch size for inference - set based on your device
        torch_dtype=torch_dtype,
        device=device,
    )

    dataset = load_dataset("distil-whisper/librispeech_long", "clean", split="validation")
    sample = dataset[0]["audio"]

    result = pipe(audio_file_path)
    return result
