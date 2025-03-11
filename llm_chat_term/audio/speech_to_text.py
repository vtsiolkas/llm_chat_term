import sys
from pathlib import Path

from openai import OpenAI

from llm_chat_term.audio.recorder import record_audio


def transcribe_speech(audio_device_idx: int, openai_api_key: str) -> str | None:
    mp3_file = record_audio(audio_device_idx)
    if not mp3_file:
        return None
    mp3_file = Path(mp3_file)

    client = OpenAI(api_key=openai_api_key)
    try:
        audio_file = mp3_file.open("rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file, language="en"
        )
        audio_file.close()
    except Exception as e:
        sys.stderr.write(f"Error transcribing audio: {e}\n")
        return None
    finally:
        mp3_file.unlink()

    result = transcription.text
    if result == "Thanks for watching!":
        return None
    return result
