from llm_chat_term.config import config, save_config
from llm_chat_term.ui.prompt_menu import Menu


def update_config(selected_audio_device: str) -> None:
    config.audio_device = selected_audio_device
    save_config(config)


def select_audio_device(audio_devices: dict[str, int]) -> str:
    options = list(audio_devices)
    menu = Menu(
        options,
        (
            " Select an audio device to record from "
            "(j/k to move, Enter to select, e to edit, d to delete, q to quit):\n"
        ),
    )

    result = menu.run()

    selected_audio_device = options[result]
    update_config(selected_audio_device)

    return selected_audio_device
