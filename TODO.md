# Project TODO List

This file tracks ongoing tasks, planned enhancements, and potential improvements for the MCP server examples and documentation.

## Documentation Improvements

- [x] Enhance `mcp_server_guide.md` for newcomers (add Getting Started, Running, schema explanations, etc.). (Commit: `9b54399`)
- [x] Update `examples/typescript-minimal/README.md` with notes on error handling and dynamic resource signature workaround. (Commit: `9b54399`)
- [x] Review `examples/python-minimal/` documentation (`README.md`, code comments) from a "zero knowledge" perspective and align `fetch-json` error handling.
- [x] Minor refinement: Explicitly mention the `/examples` directory in `mcp_server_guide.md` as runnable starting points.
- [x] Minor refinement: Consider improving the intro diagram in `mcp_server_guide.md` (optional).

## Example Enhancements

- **Sampling:**
  - [x] Python: Add a resource/tool demonstrating sampling parameters (e.g., returning different text based on `temperature`). (*Note: Tool works correctly, but testing via Cascade's direct tool calls on the background process may cause instability due to environment interaction; test with an external client.*)
  - [x] TypeScript: Add a resource/tool demonstrating sampling.
  - [x] Update relevant READMEs to explain sampling example.
- **Logging:**
  - [ ] Python: Show effective use of Python's `logging` within tool/resource handlers (different levels, context).
    *Note: Attempts to refine logging (DEBUG level, more handlers) caused runtime instability when run as a background process and were reverted.*
  - [ ] TypeScript: Show effective use of `console.log` or a simple logger within handlers.
  - [ ] Update relevant READMEs to highlight logging practices shown.
- **External APIs:**
  - [x] Python: Add a tool calling a public API (`fetch_json`) using `aiohttp`, showing async pattern and basic error handling. Mention secure API key handling (env vars).
  - [x] TypeScript: Add a tool calling a public API (`fetch-json`) using `fetch`. Mention secure API key handling.
  - [x] Update relevant READMEs with API tool example.
- **File I/O:**
  - [x] Python: Add `read_file` and `write_file` tools using `aiofiles` (async), emphasizing security/path validation.
  - [x] TypeScript: Add `readFile` and `writeFile` tools using Node.js `fs/promises`, emphasizing security.
  - [ ] Update relevant READMEs with file I/O examples and security notes.

## Code & SDK Issues

- [ ] Keep track of TypeScript SDK updates regarding type inference for `ResourceTemplate` callbacks (currently requires `handlerArgs: any`).

## Other

- [ ] (Add other tasks as they come up)
