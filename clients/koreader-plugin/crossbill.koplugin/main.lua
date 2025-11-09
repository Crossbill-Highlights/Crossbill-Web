local WidgetContainer = require("ui/widget/container/widgetcontainer")
local UIManager = require("ui/uimanager")
local InfoMessage = require("ui/widget/infomessage")
local InputDialog = require("ui/widget/inputdialog")
local DocSettings = require("docsettings")
local NetworkMgr = require("ui/network/manager")
local socket = require("socket")
local http = require("socket.http")
local https = require("ssl.https")
local ltn12 = require("ltn12")
local socketutil = require("socketutil")
local JSON = require("json")
local logger = require("logger")
local _ = require("gettext")

local CrossbillSync = WidgetContainer:extend{
    name = "Crossbill",
    is_doc_only = true,  -- Only show when document is open
}

function CrossbillSync:init()
    -- Load settings
    self.settings = G_reader_settings:readSetting("crossbill_sync") or {
        api_url = "http://localhost:8000/api/v1/highlights/upload",
    }

    self.ui.menu:registerToMainMenu(self)
end

function CrossbillSync:addToMainMenu(menu_items)
    menu_items.crossbill_sync = {
        text = _("Crossbill Sync"),
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

function CrossbillSync:configureServer()
    local input_dialog
    input_dialog = InputDialog:new{
        title = _("crossbill Server URL"),
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
                        G_reader_settings:saveSetting("crossbill_sync", self.settings)
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

function CrossbillSync:ensureWifiEnabled(callback)
    -- Enable WiFi if needed using NetworkMgr (the proper KOReader way)
    -- This will prompt user or auto-enable based on settings
    if NetworkMgr:willRerunWhenOnline(callback) then
        -- Network is off, NetworkMgr will call callback when online
        logger.info("crossbill: WiFi is off, prompting to enable...")
        return false
    else
        -- Network is already on
        logger.info("crossbill: WiFi already enabled")
        return true
    end
end

function CrossbillSync:performSync()
    -- The actual sync logic (separated so it can be called after WiFi is enabled)
    UIManager:show(InfoMessage:new{
        text = _("Syncing highlights..."),
        timeout = 2,
    })

    local success, err = pcall(function()
        -- Get book metadata
        local book_props = self.ui.doc_props
        local doc_path = self.ui.document.file

        logger.dbg("Crossbill: Syncing book:", book_props.display_title or book_props.title or doc_path)

        -- Extract ISBN from identifiers if available
        local isbn = nil
        if book_props.identifiers then
            -- Try to extract ISBN from identifiers string
            -- Note: KOReader uses backslash line continuation in the metadata file,
            -- so the identifiers are concatenated without newlines at runtime.
            -- Format: "uuid:...calibre:...ISBN:9780735211292AMAZON:..."
            -- ISBNs are numeric with possible hyphens and X (for ISBN-10)
            isbn = book_props.identifiers:match("ISBN:([%d%-X]+)")
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

        logger.dbg("Crossbill: Found", #highlights, "highlights")

        -- Send to server
        self:sendToServer(book_data, highlights)
    end)

    if not success then
        logger.err("Crossbill: Error in syncCurrentBook:", err)
        UIManager:show(InfoMessage:new{
            text = _("Error syncing book: ") .. tostring(err),
            timeout = 5,
        })
    end
end

function CrossbillSync:syncCurrentBook()
    -- Ensure WiFi is enabled before attempting to sync
    -- NetworkMgr will handle prompting user or auto-enabling based on settings
    local callback = function()
        self:performSync()
    end

    if not self:ensureWifiEnabled(callback) then
        -- WiFi is being enabled, callback will be called when ready
        logger.info("Crossbill: Waiting for WiFi to be enabled...")
    else
        -- WiFi already on, sync immediately
        self:performSync()
    end
end

function CrossbillSync:getHighlights(doc_path)
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

function CrossbillSync:sendToServer(book_data, highlights)
    -- Wrap everything in pcall for error handling
    local success, result = pcall(function()
        local payload = {
            book = book_data,
            highlights = highlights,
        }

        local body_json = JSON.encode(payload)
        logger.dbg("Crossbill: Sending request to", self.settings.api_url)
        logger.dbg("Crossbill: Payload size:", #body_json, "bytes")

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

        -- Use HTTP or HTTPS based on URL scheme
        local code, headers, status
        if self.settings.api_url:match("^https://") then
            logger.dbg("Crossbill: Using HTTPS")
            code, headers, status = socket.skip(1, https.request(request))
        else
            logger.dbg("Crossbill: Using HTTP")
            code, headers, status = socket.skip(1, http.request(request))
        end
        socketutil:reset_timeout()

        logger.dbg("Crossbill: Response code:", code)

        if code == 200 then
            local response_text = table.concat(response_body)
            logger.dbg("Crossbill: Response:", response_text)

            local ok, response_data = pcall(JSON.decode, response_text)
            if not ok then
                logger.err("Crossbill: Failed to decode JSON response:", response_text)
                return false, "Invalid server response"
            end

            UIManager:show(InfoMessage:new{
                text = string.format(
                    _("Synced successfully!\n%d new, %d duplicates"),
                    response_data.highlights_created or 0,
                    response_data.highlights_skipped or 0
                ),
                timeout = 3,
            })
            return true
        else
            logger.err("Crossbill: Sync failed with code:", code)
            UIManager:show(InfoMessage:new{
                text = _("Sync failed: ") .. tostring(code or "unknown error"),
                timeout = 3,
            })
            return false, code
        end
    end)

    if not success then
        logger.err("Crossbill: Exception during sync:", result)
        UIManager:show(InfoMessage:new{
            text = _("Sync error: ") .. tostring(result),
            timeout = 5,
        })
    end
end

function CrossbillSync:getFilename(path)
    return path:match("^.+/(.+)$") or path
end

return CrossbillSync
