import sys

from pyaudio import PyAudio

from llm_chat_term.audio.pyaudio_no_log import PyAudioNoLog
from llm_chat_term.audio.speech_to_text import transcribe_speech
from llm_chat_term.config import config
from llm_chat_term.ui.chat_ui import ChatUI
from llm_chat_term.utils import get_api_key


def get_audio_input_devices(p: PyAudio) -> dict[str, int]:
    devices: dict[str, int] = {}
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        max_input_channels = int(device_info["maxInputChannels"])
        name = str(device_info["name"])
        if max_input_channels > 0:
            devices[name] = i

    return devices


def get_user_device_idx() -> int:
    audio_device = config.audio_device
    with PyAudioNoLog() as pyaudio_initializer:
        p = pyaudio_initializer
        available_devices = get_audio_input_devices(p)
        p.terminate()

    if audio_device:
        found_audio_device = available_devices.get(audio_device)
        if found_audio_device:
            return found_audio_device

    # User hasn't selected audio device or we couldn't find it
    selected_audio_device = ChatUI.select_audio_device(available_devices)
    return available_devices[selected_audio_device]


def process_voice_command() -> str:
    openai_api_key = get_api_key("openai")
    if not openai_api_key:
        sys.stderr.write("API key for OpenAI not found.\n")
        sys.stderr.write("It is needed for transcribing audio.\n")
        return ""

    audio_device_idx = get_user_device_idx()
    captured_speech = transcribe_speech(
        audio_device_idx, openai_api_key.get_secret_value()
    )
    return captured_speech or ""
