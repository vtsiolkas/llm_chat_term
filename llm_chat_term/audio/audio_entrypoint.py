import sys

from llm_chat_term.utils import has_audio_support


def handle_voice():
    if not has_audio_support():
        sys.stderr.write("No voice support found. Install llm_chat_term[voice]\n")
        return ""

    from llm_chat_term.audio.voice_command import process_voice_command

    return process_voice_command()
