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
  - [ ] Python: Add a resource/tool demonstrating sampling parameters (e.g., returning different text based on `temperature`).
  - [ ] TypeScript: Add a resource/tool demonstrating sampling.
  - [ ] Update relevant READMEs to explain sampling example.
- **Logging:**
  - [ ] Python: Show effective use of Python's `logging` within tool/resource handlers (different levels, context).
  - [ ] TypeScript: Show effective use of `console.log` or a simple logger within handlers.
  - [ ] Update relevant READMEs to highlight logging practices shown.
- **External APIs:**
  - [ ] Python: Add a tool calling a public API (e.g., weather, jokes) using `aiohttp`, showing async pattern and basic error handling. Mention secure API key handling (env vars).
  - [ ] TypeScript: Add a tool calling a public API using `fetch`. Mention secure API key handling.
  - [ ] Update relevant READMEs with API tool example.
- **File I/O:**
  - [ ] Python: Add `read_file` and `write_file` tools using `aiofiles` (async), emphasizing security/path validation.
  - [ ] TypeScript: Add `readFile` and `writeFile` tools using Node.js `fs/promises`, emphasizing security.
  - [ ] Update relevant READMEs with file I/O examples and security notes.

## Code & SDK Issues

- [ ] Keep track of TypeScript SDK updates regarding type inference for `ResourceTemplate` callbacks (currently requires `handlerArgs: any`).

## Other

- [ ] (Add other tasks as they come up)
