# Crossbill Plugin Configuration

This document describes the configuration options for the Crossbill Anki plugin.

## Configuration Options

### server_host
- **Type**: String
- **Default**: `"http://localhost:8000"`
- **Description**: The URL of your Crossbill server. This should include the protocol (http:// or https://) and port number if needed.
- **Example**: `"https://crossbill.example.com"`

### default_deck
- **Type**: String
- **Default**: `"Default"`
- **Description**: The Anki deck where imported highlights will be added by default. You can change this for each import session.

### default_note_type
- **Type**: String
- **Default**: `"Basic"`
- **Description**: The note type to use when creating cards from highlights. Must be an existing note type in your Anki collection.
- **Supported values**: `"Basic"`, `"Basic (and reversed card)"`, or any custom note type name

### auto_tag
- **Type**: Boolean
- **Default**: `true`
- **Description**: Automatically add tags to imported notes. Tags include the book title and any tags from Crossbill.

### tag_prefix
- **Type**: String
- **Default**: `"crossbill"`
- **Description**: Prefix to add to all automatically generated tags. Helps organize and filter Crossbill-imported notes.

### last_sync
- **Type**: String (ISO 8601 datetime) or null
- **Default**: `null`
- **Description**: Timestamp of the last successful import. Used to track which highlights are new. Automatically managed by the plugin.

### ui_preferences
- **Type**: Object
- **Description**: User interface preferences for the plugin dialogs.

#### ui_preferences.dialog_width
- **Type**: Integer
- **Default**: `900`
- **Description**: Width of the highlights browser dialog in pixels.

#### ui_preferences.dialog_height
- **Type**: Integer
- **Default**: `600`
- **Description**: Height of the highlights browser dialog in pixels.

#### ui_preferences.last_selected_book
- **Type**: Integer or null
- **Default**: `null`
- **Description**: ID of the last selected book. Used to restore selection when reopening the browser. Automatically managed by the plugin.

## Editing Configuration

You can edit the configuration in two ways:

1. **Through Anki's Add-on Manager**:
   - Go to Tools → Add-ons
   - Select "Crossbill Highlights Importer"
   - Click "Config" button
   - Make your changes and save

2. **Through the Plugin's Settings Dialog**:
   - Go to Tools → Crossbill Settings
   - Modify the settings in the dialog
   - Click "Save"

## Notes

- Changes to `last_sync` and `ui_preferences.last_selected_book` are managed automatically by the plugin
- If you change `default_note_type`, make sure the note type exists in your Anki collection
- The `server_host` must be accessible from your computer (check firewall settings if needed)
- Tags are automatically sanitized to comply with Anki's tag naming rules
