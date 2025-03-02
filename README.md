# Terminal LLM Chatbot

A python terminal-based chatbot application that integrates with language models using LangChain. Features include multiline text input and streaming responses.

## Features

- Terminal-based user interface with rich text formatting
- Support for multiline text input
- Streaming responses from the language model
- Markdown rendering for assistant responses
- You can edit the conversation at any point to add/remove context
- Configurable via YAML

## Installation

You can install `llm_chat_term` by running:

```bash
uv tool install llm_chat_term
```

or if you don't have uv installed:

```bash
pip install llm_chat_term
```

### Set up your API key(s)

On first run, a `config.yaml` with default options is created in your Config dir (e.g. ~/.config/llm_chat_term)
Edit it to add your API keys and customize other options. Then re-run the application.

```
llm:
   openai_api_key: "your_openai_api_key_here""
   anthropic_key: "your_openai_api_key_here"
```

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

```
llm:
  provider: anthropic
  openai_api_key: ""
  anthropic_key: ""
  model: claude-3-7-sonnet-20250219
  temperature: 0.7
  system_prompt:
    You are a helpful assistant responding to a user's questions in a
    terminal environment. The user is an experienced software engineer, your answers
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

## Extending

To add new features:

1. Add new LLM providers by extending the `LLMClient` class
2. Customize the UI by modifying the `ChatUI` class
3. Add configuration options in `config.py`

## License

MIT
