local WidgetContainer = require("ui/widget/container/widgetcontainer")
local UIManager = require("ui/uimanager")
local InfoMessage = require("ui/widget/infomessage")
local InputDialog = require("ui/widget/inputdialog")
local DocSettings = require("docsettings")
local https = require("ssl.https")
local ltn12 = require("ltn12")
local socketutil = require("socketutil")
local JSON = require("json")
local _ = require("gettext")

local InkwellSync = WidgetContainer:extend{
    name = "inkwell",
    is_doc_only = true,  -- Only show when document is open
}

function InkwellSync:init()
    -- Load settings
    self.settings = G_reader_settings:readSetting("inkwell_sync") or {
        api_url = "http://localhost:8000/api/v1/highlights/upload",
    }

    self.ui.menu:registerToMainMenu(self)
end

function InkwellSync:addToMainMenu(menu_items)
    menu_items.inkwell_sync = {
        text = _("Inkwell Sync"),
        sub_item_table = {
            {
                text = _("Sync Current Book"),
                callback = function()
                    self:syncCurrentBook()
                end,
            },
            {
                text = _("Configure Server"),
                callback = function()
                    self:configureServer()
                end,
            },
        },
    }
end

function InkwellSync:configureServer()
    local input_dialog
    input_dialog = InputDialog:new{
        title = _("Inkwell Server URL"),
        input = self.settings.api_url,
        input_type = "text",
        buttons = {
            {
                {
                    text = _("Cancel"),
                    callback = function()
                        UIManager:close(input_dialog)
                    end,
                },
                {
                    text = _("Save"),
                    is_enter_default = true,
                    callback = function()
                        self.settings.api_url = input_dialog:getInputText()
                        G_reader_settings:saveSetting("inkwell_sync", self.settings)
                        UIManager:close(input_dialog)
                        UIManager:show(InfoMessage:new{
                            text = _("Server URL saved"),
                        })
                    end,
                },
            },
        },
    }
    UIManager:show(input_dialog)
    input_dialog:onShowKeyboard()
end

function InkwellSync:syncCurrentBook()
    UIManager:show(InfoMessage:new{
        text = _("Syncing highlights..."),
        timeout = 2,
    })

    -- Get book metadata
    local book_props = self.ui.doc_props
    local doc_path = self.ui.document.file

    -- Extract ISBN from identifiers if available
    local isbn = nil
    if book_props.identifiers then
        -- Try to extract ISBN from identifiers string
        -- Format: "uuid:...\ncalibre:...\nISBN:9780735211292\n..."
        for identifier in string.gmatch(book_props.identifiers, "[^\n]+") do
            if identifier:match("^ISBN:") then
                isbn = identifier:gsub("^ISBN:", "")
                break
            end
        end
    end

    local book_data = {
        title = book_props.display_title or book_props.title or self:getFilename(doc_path),
        author = book_props.authors or nil,
        isbn = isbn,
    }

    -- Get highlights
    local highlights = self:getHighlights(doc_path)

    if not highlights or #highlights == 0 then
        UIManager:show(InfoMessage:new{
            text = _("No highlights found in this book"),
        })
        return
    end

    -- Send to server
    self:sendToServer(book_data, highlights)
end

function InkwellSync:getHighlights(doc_path)
    local doc_settings = DocSettings:open(doc_path)
    local results = {}

    -- Try modern annotations format first
    local annotations = doc_settings:readSetting("annotations")
    if annotations then
        for _, annotation in ipairs(annotations) do
            table.insert(results, {
                text = annotation.text or "",
                note = annotation.note or nil,
                datetime = annotation.datetime or "",
                page = annotation.pageno,
                chapter = annotation.chapter or nil,
            })
        end
        return results
    end

    -- Fallback to legacy format
    local highlights = doc_settings:readSetting("highlight")
    if not highlights then
        return nil
    end

    local bookmarks = doc_settings:readSetting("bookmarks") or {}

    for page, items in pairs(highlights) do
        for _, item in ipairs(items) do
            local note = nil

            -- Find matching bookmark for note
            for _, bookmark in pairs(bookmarks) do
                if bookmark.datetime == item.datetime then
                    note = bookmark.text or nil
                    break
                end
            end

            table.insert(results, {
                text = item.text or "",
                note = note,
                datetime = item.datetime or "",
                page = item.page,
                chapter = item.chapter or nil,
            })
        end
    end

    return results
end

function InkwellSync:sendToServer(book_data, highlights)
    local payload = {
        book = book_data,
        highlights = highlights,
    }

    local body_json = JSON.encode(payload)
    local response_body = {}

    local request = {
        url = self.settings.api_url,
        method = "POST",
        headers = {
            ["Content-Type"] = "application/json",
            ["Accept"] = "application/json",
            ["Content-Length"] = tostring(#body_json),
        },
        source = ltn12.source.string(body_json),
        sink = ltn12.sink.table(response_body),
    }

    local code, headers, status = socket.skip(1, https.request(request))
    socketutil:reset_timeout()

    if code == 200 then
        local response_text = table.concat(response_body)
        local response_data = JSON.decode(response_text)

        UIManager:show(InfoMessage:new{
            text = string.format(
                _("Synced successfully!\n%d new, %d duplicates"),
                response_data.highlights_created or 0,
                response_data.highlights_skipped or 0
            ),
            timeout = 3,
        })
    else
        UIManager:show(InfoMessage:new{
            text = _("Sync failed: ") .. tostring(code),
            timeout = 3,
        })
    end
end

function InkwellSync:getFilename(path)
    return path:match("^.+/(.+)$") or path
end

return InkwellSync
