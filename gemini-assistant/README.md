# Adaptive AI Personal Assistant (Gemini API)

A modular CLI-based personal assistant built around Google Gemini function calling.

## Architecture

The project is intentionally split by responsibility:

- `adaptive_assistant/agent.py`: ReAct orchestration (`Reason -> Act -> Observe`)
- `adaptive_assistant/memory.py`: Session conversation memory
- `adaptive_assistant/registry.py`: Tool factory/registry and execution boundary
- `adaptive_assistant/tools/base.py`: Tool abstraction (Open/Closed + DIP)
- `adaptive_assistant/llm_client.py`: Gemini API client and response parsing
- `adaptive_assistant/tools/`: Concrete tool strategies

### Applied Patterns

- **Strategy Pattern**: each tool class is an interchangeable strategy.
- **Factory/Registry Pattern**: `ToolRegistry` maps tool name to implementation.
- **ReAct Loop**: model reasons, requests tool calls, observes outputs, then answers.

## Implemented Tools

Total tools: **5**

1. `calculator`
2. `current_time`
3. `weather_lookup`
4. `read_local_file` (custom)
5. `text_stats` (custom)

## Setup

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Set API key

Windows PowerShell:

```powershell
$env:GEMINI_API_KEY="your_api_key"
```

Windows CMD:

```cmd
set GEMINI_API_KEY=your_api_key
```

Linux/macOS:

```bash
export GEMINI_API_KEY="your_api_key"
```

## Run

```bash
python main.py
```

## Practical Demo

To test the tools without the Gemini API, run the demo script:

```bash
python practical_demo.py
```

This demonstrates calculator, file reader, text stats, and time tools.

## Suggested Test Prompts

- "What time is it right now?"
- "Calculate (45 + 15) * 2 / 3"
- "What is the weather in Riga?"
- "Read the first part of README.md"
- "Analyze this text: Architecture matters because maintainability matters."
- "Use tools if needed: summarize README.md in 3 bullets and count the words in the summary"

## Error-Handling Coverage

- Gemini API key missing / API failures
- Unknown tool names returned by model
- Invalid tool arguments (type mismatch/missing args)
- Tool runtime failures (network/file access)
- Multi-tool model turns in a single reasoning step

## Notes

- `read_local_file` is restricted to the current project root for safety.
- Conversation context is maintained for the session through the agent's Gemini chat session and in-process memory log.
- Gemini client creation is lazy, so startup succeeds even if the API key is missing and the error is surfaced on first use.

## Verification

Run the focused architecture checks with:

```bash
python -m unittest discover -s tests -p "test_*.py"
```
