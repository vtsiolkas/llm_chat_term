import sys
import tempfile
import warnings
import wave
from pathlib import Path

import pyaudio
from pydub import AudioSegment

from llm_chat_term.audio.pyaudio_no_log import PyAudioNoLog

# Silence tye pydub warnings coming from broken regexes
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pydub.utils")


def record_audio(
    audio_device_idx: int,
    sample_rate: int = 16000,
    channels: int = 1,
    chunk: int = 1024,
) -> str | None:
    """Record audio from microphone until Ctrl+C and save as MP3"""
    # Initialize PyAudio, capturing stdout and stderr to avoid it
    # flooding the console with warnings
    with PyAudioNoLog() as pyaudio_initializer:
        p = pyaudio_initializer

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
        temp_wav = temp.name
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp:
        temp_mp3 = temp.name

    sys.stdout.write("Recording... Press Ctrl+C to stop")
    sys.stdout.flush()
    try:
        # Open stream
        stream = p.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            input=True,
            input_device_index=audio_device_idx,
            frames_per_buffer=chunk,
        )
    except Exception as e:
        sys.stderr.write(f"Error capturing audio: {e}\n")
        return None

    frames: list[bytes] = []

    try:
        while True:
            data = stream.read(chunk)
            frames.append(data)
    except KeyboardInterrupt:
        sys.stdout.write("\033[2K")  # Clear the entire line and return to start
        sys.stdout.flush()
        sys.stdout.write("Recording stopped. Transcribing audio...\n")
    finally:
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        p.terminate()

    if frames:
        # Save as WAV first (temporary)
        wf = wave.open(temp_wav, "wb")  # noqa: SIM115
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b"".join(frames))
        wf.close()

        # Convert to MP3
        sound = AudioSegment.from_wav(temp_wav)
        sound.export(
            temp_mp3,
            format="mp3",
            bitrate="64k",
            parameters=["-ac", "1", "-ar", "16000"],
        )

        # Remove temporary WAV file
        Path(temp_wav).unlink()
        return temp_mp3

    sys.stderr.write("Failed to capture audio...\n")
    return None
