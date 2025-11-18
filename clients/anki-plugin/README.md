# Crossbill Anki Plugin

Import your reading highlights from Crossbill server into Anki as flashcards for spaced repetition learning.

## Features

- 🔍 Browse and search highlights from your Crossbill library
- 📚 View highlights organized by books and chapters
- 🎴 Convert highlights into Anki flashcards ✓
- ⚙️ Configurable server connection
- 🏷️ Auto-tagging with book metadata ✓
- ✅ Duplicate detection and prevention ✓
- 🎯 Custom deck and note type selection ✓

## Current Status

**Stage 1: Foundation & Basic Setup** ✓
**Stage 2: Note Creation & Import** ✓

The plugin currently supports:
- ✅ Browsing books from your Crossbill server
- ✅ Viewing highlights with full details (text, notes, tags, page numbers)
- ✅ Configurable server URL and connection testing
- ✅ Creating Anki notes from highlights
- ✅ Multi-select highlights with checkboxes
- ✅ Deck and note type selection
- ✅ Duplicate detection (prevents re-importing)
- ✅ Auto-tagging with book, author, and highlight tags
- ✅ Visual import status (shows which highlights are imported)
- ✅ Batch import with progress tracking

**Coming Soon** (Stage 3):
- Search and filter highlights
- Batch import entire books/chapters
- Custom note type field mapping
- Sync tracking

## Installation

### For Development/Testing

1. Clone or download the Crossbill repository

2. Locate your Anki add-ons directory:
   - **Windows**: `%APPDATA%\Anki2\addons21\`
   - **Mac**: `~/Library/Application Support/Anki2/addons21/`
   - **Linux**: `~/.local/share/Anki2/addons21/`

3. Create a symbolic link or copy the plugin folder:
   ```bash
   # Option 1: Symbolic link (recommended for development)
   ln -s /path/to/Crossbill/clients/anki-plugin /path/to/Anki2/addons21/crossbill

   # Option 2: Copy the folder
   cp -r /path/to/Crossbill/clients/anki-plugin /path/to/Anki2/addons21/crossbill
   ```

4. Restart Anki

5. The plugin should appear in Tools → Add-ons

### From AnkiWeb (Future)

Once published to AnkiWeb:
1. Open Anki → Tools → Add-ons → Get Add-ons
2. Enter the add-on code
3. Restart Anki

## Configuration

### Initial Setup

1. In Anki, go to **Tools → Crossbill Settings**
2. Enter your Crossbill server URL (e.g., `http://localhost:8000`)
3. Click **Test Connection** to verify it works
4. Click **Save**

### Configuration Options

Edit configuration via **Tools → Add-ons → Crossbill → Config**:

- **server_host**: URL of your Crossbill server
- **default_deck**: Default Anki deck for imported notes
- **default_note_type**: Default note type to use (e.g., "Basic")
- **auto_tag**: Automatically add tags to imported notes
- **tag_prefix**: Prefix for auto-generated tags (default: "crossbill")

See [config.md](config.md) for detailed configuration documentation.

## Usage

### Browse Highlights

1. Go to **Tools → Browse Crossbill Highlights**
2. Select a book from the books list at the top
3. Browse highlights in the middle section
4. Click on a highlight to see full details in the bottom section

### Create Flashcards

1. Open the highlights browser (**Tools → Browse Crossbill Highlights**)
2. Select a book to see its highlights
3. Use checkboxes to select highlights you want to import:
   - Click individual checkboxes, or
   - Use "Select All" to select all highlights, or
   - Use "Deselect All" to clear selections
4. Choose your target **Deck** from the dropdown
5. Choose your **Note Type** (e.g., "Basic", "Basic (and reversed card)")
6. Click **Import Selected Highlights**
7. Confirm the import
8. Wait for the import to complete (progress dialog will show)

**Notes:**
- Already imported highlights are marked with "✓ Imported" and grayed out
- Duplicate detection prevents re-importing the same highlight
- Each highlight creates one note with:
  - **Front**: The highlight text
  - **Back**: Book title, author, chapter, page, and your notes
- Tags are automatically added (book name, author, Crossbill tags)
- You can import to any deck and use any note type in your collection

## Prerequisites

### Crossbill Server

You need a running Crossbill server with highlights. The server must be accessible from your computer where Anki is installed.

### CORS Configuration

The Crossbill backend must allow CORS requests from Anki. By default, the backend allows all origins (`*`), which works for desktop applications.

If you need to restrict CORS:
```bash
# In backend/.env
CORS_ORIGINS=*  # Recommended for desktop apps
```

## Troubleshooting

### "Failed to connect to server"

1. Check that your Crossbill server is running
2. Verify the server URL in settings (include `http://` or `https://`)
3. Check firewall settings
4. Try the **Test Connection** button in settings

### "No books found"

1. Make sure you have books with highlights in your Crossbill library
2. Check that the API endpoints are working:
   - `http://your-server:8000/api/v1/highlights/books`
3. Check server logs for errors

### Plugin doesn't appear in Anki

1. Verify the plugin is in the correct add-ons directory
2. Check the folder name is `crossbill`
3. Restart Anki completely
4. Check **Tools → Add-ons** for error messages

### Import errors (for development)

If you see Python import errors:
1. Make sure all `.py` files are in the plugin directory
2. Check that `__init__.py` exists in the plugin root and `ui/` folder
3. Restart Anki to reload the plugin

## Development

### Project Structure

```
clients/anki-plugin/
├── __init__.py              # Plugin entry point
├── manifest.json            # Plugin metadata
├── config.json              # Default configuration
├── config.md                # Config documentation
├── README.md                # This file
├── implementation_plan.md   # Development plan
├── api.py                   # Crossbill API client
├── models.py                # Data models
└── ui/
    ├── __init__.py
    ├── settings_dialog.py   # Settings dialog
    └── browser_dialog.py    # Highlights browser
```

### Testing

1. Make changes to the plugin code
2. Restart Anki to reload the plugin
3. Test functionality through the UI
4. Check Anki's console for error messages (Tools → Add-ons → View Files)

### Debugging

Enable Anki's debug console:
1. Help → About → Copy Debug Info (to see Python version and Anki version)
2. Tools → Add-ons → [Select Crossbill] → View Files (to see plugin directory)
3. Check `~/.local/share/Anki2/addons21/crossbill/` for log files

## API Reference

This plugin uses the Crossbill API:

- **GET /api/v1/highlights/books**: List books with highlight counts
- **GET /api/v1/book/{book_id}**: Get book with chapters and highlights

## Roadmap

See [implementation_plan.md](implementation_plan.md) for the complete development roadmap.

### Stage 2: Note Creation ✓
- [x] Create Anki notes from highlights
- [x] Basic note type support
- [x] Duplicate prevention
- [x] Deck selection

### Stage 3: Enhanced Features (Next)
- [ ] Search and filter highlights
- [ ] Batch import entire books/chapters
- [ ] Custom note type field mapping
- [ ] Sync tracking

### Stage 4: Polish
- [ ] Cloze deletion support
- [ ] Advanced tag management
- [ ] Performance optimizations
- [ ] Comprehensive documentation

## Contributing

Contributions are welcome! Please see the main [Crossbill repository](https://github.com/Tumetsu/Crossbill) for contribution guidelines.

## License

MIT License - See the main Crossbill repository for details.

## Support

For issues and feature requests, please visit the [Crossbill repository](https://github.com/Tumetsu/Crossbill/issues).

## Acknowledgments

- Built for [Anki](https://apps.ankiweb.net/), the powerful spaced repetition software
- Part of the [Crossbill](https://github.com/Tumetsu/Crossbill) project
- Inspired by the Crossbill Obsidian plugin

## Changelog

### v0.2.0 (Stage 2) - Current

- ✅ Create Anki notes from highlights
- ✅ Multi-select highlights with checkboxes
- ✅ Deck and note type selection
- ✅ Duplicate detection and prevention
- ✅ Auto-tagging (book, author, highlight tags)
- ✅ Visual import status (shows imported highlights)
- ✅ Batch import with progress tracking
- ✅ Support for Basic and custom note types
- ✅ Import statistics (created/skipped/failed)

### v0.1.0 (Stage 1)

- ✅ Initial plugin structure
- ✅ Server configuration dialog
- ✅ Browse books and highlights
- ✅ View highlight details
- ✅ Connection testing
- ✅ Vertical layout with full-width sections

### Planned for v0.3.0 (Stage 3)

- Search and filter highlights
- Batch import entire books/chapters
- Custom note type field mapping
- Sync tracking
