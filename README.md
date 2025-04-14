# MCP Server Guide & Examples

A comprehensive guide and collection of example implementations for building Model Context Protocol (MCP) servers. This repository demonstrates how to create MCP servers in multiple languages, with a focus on Python and TypeScript.

## 🚀 Features

- **Complete Server Examples:**
  - Python minimal server with async support
  - TypeScript minimal server with ES modules
  - Both implementations showcase core MCP concepts

- **Core Functionality Examples:**
  - Tools (calculate, fetch-json, file I/O)
  - Resources (static and dynamic)
  - Prompts and templates
  - Logging and error handling

- **Security & Best Practices:**
  - Sandboxed file operations
  - Error handling patterns
  - Logging strategies
  - Type safety (TypeScript/Pydantic)

## 📚 Documentation

- [Server Guide](mcp_server_guide.md) - Main documentation and tutorial
- [Python Example](examples/python-minimal/README.md) - Python implementation details
- [TypeScript Example](examples/typescript-minimal/README.md) - TypeScript implementation details

## 🛠️ Quick Start

1. Choose your preferred implementation:
   ```bash
   # Python
   cd examples/python-minimal
   pip install -r requirements.txt
   python server.py

   # TypeScript
   cd examples/typescript-minimal
   npm install
   npm run build
   npm start
   ```

2. Connect using the MCP CLI:
   ```bash
   mcp-cli connect
   ```

## 📋 Prerequisites

- Python 3.8+ (for Python example)
- Node.js 16+ (for TypeScript example)
- MCP CLI tool (`npm install -g @modelcontextprotocol/cli`)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the ISC License - see the LICENSE file for details.
