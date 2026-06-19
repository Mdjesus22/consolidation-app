"""
Simple command-driven agent using Anthropic API.
Commands: "commit this", "delete file.txt", "list files", "read file.txt", etc.

Setup:
  pip install anthropic
  set ANTHROPIC_API_KEY=your_key_here   (Windows)
  export ANTHROPIC_API_KEY=your_key_here (Mac/Linux)

Run:
  python agent.py
"""

import anthropic
import subprocess
import os

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

# ── Tools the agent can call ──────────────────────────────────────────────────

TOOLS = [
    {
        "name": "run_shell",
        "description": "Run any shell command (git commit, mkdir, etc.)",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to run"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "delete_file",
        "description": "Delete a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "read_file",
        "description": "Read a file's contents",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "list_files",
        "description": "List files in a directory",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path (default: current)"}
            },
            "required": []
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["path", "content"]
        }
    }
]

# ── Tool executor ─────────────────────────────────────────────────────────────

def execute_tool(name, inputs):
    print(f"  [tool] {name}({inputs})")

    if name == "run_shell":
        result = subprocess.run(
            inputs["command"], shell=True,
            capture_output=True, text=True, cwd=os.getcwd()
        )
        return result.stdout or result.stderr or "(no output)"

    elif name == "delete_file":
        path = inputs["path"]
        if os.path.exists(path):
            os.remove(path)
            return f"Deleted {path}"
        return f"File not found: {path}"

    elif name == "read_file":
        path = inputs["path"]
        if os.path.exists(path):
            with open(path) as f:
                return f.read()
        return f"File not found: {path}"

    elif name == "list_files":
        path = inputs.get("path", ".")
        files = os.listdir(path)
        return "\n".join(files)

    elif name == "write_file":
        with open(inputs["path"], "w") as f:
            f.write(inputs["content"])
        return f"Written to {inputs['path']}"

    return "Unknown tool"

# ── Agent loop ────────────────────────────────────────────────────────────────

def run_agent(user_command: str):
    messages = [{"role": "user", "content": user_command}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=TOOLS,
            messages=messages
        )

        # If Claude wants to call a tool
        if response.stop_reason == "tool_use":
            # Add Claude's response to history
            messages.append({"role": "assistant", "content": response.content})

            # Execute each tool call and collect results
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            messages.append({"role": "user", "content": tool_results})

        else:
            # Final text response
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Agent ready. Type your command (or 'quit' to exit).\n")
    while True:
        command = input("You: ").strip()
        if command.lower() in ("quit", "exit"):
            break
        if not command:
            continue
        answer = run_agent(command)
        print(f"Agent: {answer}\n")

if __name__ == "__main__":
    main()
