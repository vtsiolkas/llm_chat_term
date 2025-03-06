# Terminal LLM Chatbot

A python terminal-based chatbot application that integrates with language models using LangChain. Features include multiline text input and streaming responses.

## Features

- Terminal-based user interface with rich text formatting
- Support for multiline text input
- Streaming responses from the language model
- Markdown rendering for assistant responses
- You can edit the conversation at any point to add/remove context
- Configurable via YAML
- Supports Claude 3.7 (with optional extended thinking), ChatGPT-4o and o3-mini
- Change models/chats on the fly

## Installation

You can install `llm_chat_term` using [uv](https://github.com/astral-sh/uv) by running:

```bash
uv tool install llm_chat_term
```

or if you don't have uv installed:

```bash
pip install llm_chat_term
# or
pipx install llm_chat_term
```

### Set up your API key(s)

On first run, a `config.yaml` with default options is created in your Config dir (e.g. ~/.config/llm_chat_term)
Edit it to add your API keys and customize other options. Then re-run the application.

## Usage

Run the chatbot from the command line:

```
llm_chat_term
```

### Controls

- Type your message and press `Alt(Esc)+Enter` to send
- Use `Enter` to add a new line in your message
- Type `/exit`, `exit`, or press `Ctrl+D` to exit the application
- Type `/help` to view help for available commands
- Press `Ctrl+C` to interrupt and exit

## Configuration

The following environment variables can be set in the `config.yaml` file:

```yaml
llm:
  models:
    - provider: anthropic
      model: claude-3-7-sonnet-20250219
      api_key: ""
      temperature:
    - provider: openai
      model: gpt-4o
      api_key: ""
      temperature:
    - provider: openai
      model: o3-mini
      api_key: ""
      temperature:
  system_prompt:
    You are a helpful assistant responding to a user's questions in a PC
    terminal application. The user is an experienced software engineer, your answers
    should be concise and not repetitive. Skip conclusions and summarizations of your
    answers.If the user asks for a change in code, don't return the whole code, just
    the changed segment(s).
ui:
  prompt_symbol: ">>> "
  user: user
  assistant: assistant
colors:
  user: cyan
  assistant: grey39
  system: yellow
```

## License

MIT
