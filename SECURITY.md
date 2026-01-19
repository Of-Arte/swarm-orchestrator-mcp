# Security Policy


## Security Considerations

### API Keys

- **Never commit API keys** to version control
- Use environment variables: `GEMINI_API_KEY`, `OPENAI_API_KEY`
- Consider using a `.env` file (add to `.gitignore`)

### Automated Code Execution

Swarm v3.0 includes capabilities that execute code or commands:

- **`orchestrator.py debug` (SBFL)**: Runs the test command provided by the user (e.g., `pytest`). Ensure you trust the test suite of the project you are debugging.
- **Toolchain Manager**: Can execute build/lint commands.

**Best Practice:** Only run Swarm on projects/codebases you trust.

### File System Access

- **OCC Validator**: Performs atomic writes to files.
- **HippoRAG**: Reads and parses all `.py` files in the directory.
- **Swarm Cache**: Data is stored in `.swarm-cache/`.

### Docker

- The container runs as non-root by default
- Mount volumes carefully when using `-v`
- Do not expose the container to untrusted networks

## Best Practices

1. **Keep dependencies updated**: `pip install --upgrade -r requirements.txt`
2. **Review before running**: Be aware of what `debug` and `run` commands will execute.
3. **Use file permissions**: Restrict access to `.swarm-cache/`
4. **Audit API usage**: Monitor embedding/LLM API calls for unexpected activity
