# Project TODO List

This file tracks ongoing tasks, planned enhancements, and potential improvements for the MCP server examples and documentation.

## Documentation Improvements

- [x] Enhance `mcp_server_guide.md` for newcomers (add Getting Started, Running, schema explanations, etc.). (Commit: `9b54399`)
- [x] Update `examples/typescript-minimal/README.md` with notes on error handling and dynamic resource signature workaround. (Commit: `9b54399`)
- [x] Review `examples/python-minimal/` documentation (`README.md`, code comments) from a "zero knowledge" perspective and align `fetch-json` error handling.
- [x] Minor refinement: Explicitly mention the `/examples` directory in `mcp_server_guide.md` as runnable starting points.
- [x] Minor refinement: Consider improving the intro diagram in `mcp_server_guide.md` (optional).

## Example Enhancements

- [ ] Add more complex/realistic examples:
    - [ ] Example demonstrating server-side sampling (if client supports).
    - [ ] Example using logging capabilities.
    - [ ] Example tool interacting with a real external API (requires handling secrets/auth).
    - [ ] Example resource reading from/writing to a local file (consider security implications).

## Code & SDK Issues

- [ ] Investigate `FastMCP` vs `Server` class naming in python `mcp-sdk` (used in example vs mentioned in guide).
- [ ] Keep track of TypeScript SDK updates regarding type inference for `ResourceTemplate` callbacks (currently requires `handlerArgs: any`).

## Other

- [ ] (Add other tasks as they come up)
