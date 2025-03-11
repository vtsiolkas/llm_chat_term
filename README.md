# Terminal LLM Chatbot

A python terminal-based chatbot application that integrates with language models. Features include multiline text input, streaming responses and many commands to control the conversation.

## Features

- Supports Claude 3.7 (with optional extended thinking), ChatGPT-4o and o3-mini
- Terminal-based user interface with rich text formatting and code highlighting
- Support for multiline text input
- Streaming responses from the language model
- Conversations are saved as text files for portability and easy manipulation
- Anonymous chats that don't get saved anywhere
- You can edit the conversation at any point to add/remove context or edit the system prompt
- Change active model/conversation on the fly
- Embed files from the filesystem or webpage contents by url in your prompts
- Quick temporary prompts that don't pollute the current conversation context
- Optional voice input support (install llm-chat-term[voice])
- Configurable via a YAML config file

## Installation

You can install `llm-chat-term` using [uv](https://github.com/astral-sh/uv) by running:

```bash
uv tool install llm-chat-term
```

or if you don't have uv installed:

```bash
pip install llm-chat-term
# or
pipx install llm-chat-term
```

If you want voice input support, you will need to have `portaudio` and `ffmpeg` installed for your system. Then, install the `llm_chat_term[voice]` instead of the base `llm_chat_term` package.

### Set up your API key(s)

On first run, a `config.yaml` with default options is created in your Config dir (e.g. ~/.config/llm_chat_term)
Edit it to add your API key(s) and customize other options. Then re-run the application.

Alternatively the application can read your API keys from your env (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`)

## Usage

Run the chatbot from the command line:

```
llm_chat_term
```

### Controls

- Type your message and press `Alt(Esc)+Enter` to send
- Use `Enter` to add a new line in your message
- Type `:exit` or press `Ctrl+D` to exit the application
- Type `:help` to view help for available commands
- Press `Ctrl+C` to interrupt and exit

### Commands

- `:help`
  Displays help about the commands.
- `:info`
  Displays info about this chat.
- `:edit`, `:e`
  Opens the conversation history in $EDITOR (vim by default).
  Edit it and save and it will be reloaded in the message history.
  You can edit the system prompt for the current conversation this way.
- `:chat`
  Display a menu to select a different chat.
- `:model`
  Display a menu to select a different chat.
- `:redraw`
  Redraw the whole conversation.
- `:tmp {prompt}`
  This prompt won't be saved to the conversation history.
  Ideal for quick one-off questions in the middle of a large conversation
- `:think {prompt}`
  Enable thinking mode only for this question (Claude only).
- `:read {path}`
  Embed a text file in the prompt (replaces the line with :read).
- `:web {url}`
  Embed a webpage contents in the prompt (replaces the line with :web).
- `:exit`
  Exits the application. The conversation is saved if not anonymous chat.

## Configuration

This is the initial `config.yaml` file:

````yaml
llm:
  models:
    - provider: anthropic
      name: claude-3-7-sonnet-20250219
      temperature: null
    - provider: openai
      name: o3-mini
      temperature: null
    - provider: openai
      name: gpt-4o
      temperature: null
  api_keys:
    - provider: anthropic
      api_key: ""
    - provider: openai
      api_key: ""
  system_prompt:
    "You are a helpful assistant responding to a user's questions in
    a PC terminal application.

    The user is an experienced software engineer, your answers should be concise and
    not repetitive.

    Skip conclusions and summarizations of your answers.

    If the user asks for a change in code, don't return the whole code, just the
    changed segment(s).

    Return your answers in markdown format, and wrap code in ``` blocks.
    "
ui:
  prompt_symbol: ">>> "
  user: user
  assistant: assistant
colors:
  user: cyan
  assistant: grey39
  system: yellow
````

## License

MIT
