# Crossbill KOReader Plugin

Syncs your KOReader highlights to your crossbill server.

## Installation

1. Copy the `crossbill.koplugin` directory to your KOReader plugins folder:
   - **Device**: `koreader/plugins/`
   - **Desktop**: `.config/koreader/plugins/` (Linux/Mac) or `%APPDATA%\koreader\plugins\` (Windows)

2. Restart KOReader

3. Open any book and go to: Menu → crossbill Sync → Configure Server

4. Enter your crossbill server URL (e.g., `http://192.168.1.100:8000/api/v1/highlights/upload`)

## Usage

1. Open a book with highlights
2. Menu → crossbill Sync → Sync Current Book
3. View your synced highlights on your crossbill server

## Features

- Syncs highlights from the currently open book
- Automatic deduplication - re-syncing won't create duplicates
- Supports both modern and legacy KOReader annotation formats
- Extracts ISBN from book metadata when available
- Works with any book format supported by KOReader (EPUB, PDF, etc.)

## Requirements

- KOReader version 2021.04 or later
- Network connection to your crossbill server

## Server Configuration

The default server URL is `http://localhost:8000/api/v1/highlights/upload`. You'll need to change this to your actual crossbill server address.

For testing on the same device where KOReader is running:
- Use `http://localhost:8000/api/v1/highlights/upload`

For syncing to a server on your local network:
- Use `http://<server-ip>:8000/api/v1/highlights/upload`
- Example: `http://192.168.1.100:8000/api/v1/highlights/upload`

## Troubleshooting

### "No highlights found in this book"
- Make sure you've actually highlighted some text in the current book
- Try creating a new highlight to verify the feature is working

### "Sync failed: XXX"
- Check that the server URL is correct
- Verify the crossbill server is running and accessible
- Check your network connection
- Look at the error code:
  - `nil` or timeout errors: Network/connection issue
  - `404`: Incorrect URL
  - `500`: Server error (check server logs)

### Changes not appearing on server
- The plugin only syncs when you explicitly trigger it
- If highlights show as "duplicates", they were already synced previously
- Check the success message for the count of new vs duplicate highlights
