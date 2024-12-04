# testCal MCP server

<div align="center">
  <a href="https://youtu.be/EJ8z1nQ8HcY">
    <img src="https://img.youtube.com/vi/EJ8z1nQ8HcY/maxresdefault.jpg" alt="Watch the Tutorial" style="max-width:100%;">
  </a>
  <p><em>Click the image above to watch the tutorial!</em></p>
</div>

This Custom MCP Server helps me get and set meeting appointment in my calendar.

## Components

### Resources

The server implements a simple note storage system with:
- Custom note:// URI scheme for accessing individual notes
- Each note resource has a name, description and text/plain mimetype

### Prompts

The server provides a single prompt:
- summarize-notes: Creates summaries of all stored notes
  - Optional "style" argument to control detail level (brief/detailed)
  - Generates prompt combining all current notes with style preference

### Tools

The server implements one tool:
- add-note: Adds a new note to the server
  - Takes "name" and "content" as required string arguments
  - Updates server state and notifies clients of resource changes

## Configuration

[TODO: Add configuration details specific to your implementation]

## Quickstart

### Install

Create a Google Desktop Application OAuth2 Client and download the Client_id & Client_secret JSON and save it as credentials.json in the root of this repo.

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```
  "mcpServers": {
    "testCal": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/avijitsarkar/Library/Application Support/Claude/testCal",
        "run",
        "testCal"
      ]
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  ```
  "mcpServers": {
    "testCal": {
      "command": "uvx",
      "args": [
        "testCal"
      ]
    }
  }
  ```
</details>

## Development

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:
```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:
- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).


You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /Users/avijitsarkar/Library/Application Support/Claude/testCal run testcal
```


Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.

### Community and Support
- Join our community: [Kno2gether Community](https://community.kno2gether.com)
- Full Course (50% OFF): [End-to-End SaaS Launch Course](https://knolabs.biz/course-at-discount)

### Hosting Partners
- [Kamatera - Get $100 Free VPS Credit](https://knolabs.biz/100-dollar-free-credit)
- [Hostinger - Additional 20% Discount](https://knolabs.biz/20-Percent-Off-VPS)

## 📺 Video Tutorials

Follow along with our detailed video tutorials on the [Kno2gether YouTube Channel](https://youtube.com/@kno2gether) for step-by-step guidance and best practices.

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.