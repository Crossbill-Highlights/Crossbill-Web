--[[
Crossbill Sync Plugin for KOReader

A plugin to synchronize book highlights with a Crossbill server.
Supports manual sync, auto-sync on suspend/exit, and cover image uploads.
]]

local WidgetContainer = require("ui/widget/container/widgetcontainer")
local logger = require("logger")

local Settings = require("modules/settings")
local Network = require("modules/network")
local Auth = require("modules/auth")
local ApiClient = require("modules/api_client")
local HighlightExtractor = require("modules/highlight_extractor")
local BookMetadata = require("modules/book_metadata")
local UI = require("modules/ui")

local CrossbillSync = WidgetContainer:extend({
	name = "Crossbill",
	is_doc_only = true, -- Only show when document is open
})

--- Initialize the plugin
function CrossbillSync:init()
	-- Initialize settings
	self.settings = Settings:new():load()

	-- Initialize authentication with settings
	self.auth = Auth:new(self.settings)

	-- Initialize API client with settings and auth
	self.api_client = ApiClient:new(self.settings, self.auth)

	-- Register menu
	self.ui.menu:registerToMainMenu(self)
end

--- Add plugin menu items to KOReader main menu
function CrossbillSync:addToMainMenu(menu_items)
	menu_items.crossbill_sync = UI.buildMenuItems({
		on_sync = function()
			self:syncCurrentBook()
		end,
		on_configure = function()
			self:configureServer()
		end,
		is_autosync_enabled = function()
			return self.settings:isAutosyncEnabled()
		end,
		on_toggle_autosync = function()
			local enabled = self.settings:toggleAutosync()
			UI.showAutosyncToggled(enabled)
		end,
	})
end

--- Show server configuration dialog
function CrossbillSync:configureServer()
	UI.showConfigureServerDialog(self.settings)
end

--- Sync the currently open book's highlights
-- @param is_autosync boolean If true, run in silent mode (no UI feedback)
function CrossbillSync:syncCurrentBook(is_autosync)
	local callback = function()
		self:performSync(is_autosync)
	end

	if not Network.ensureWifiEnabled(callback) then
		-- WiFi is being enabled, callback will be called when ready
		logger.info("Crossbill: Waiting for WiFi to be enabled...")
	else
		-- WiFi already on, sync immediately
		self:performSync(is_autosync)
	end
end

--- Perform the actual sync operation
-- @param is_autosync boolean If true, run in silent mode
function CrossbillSync:performSync(is_autosync)
	-- Safety check: ensure document is available
	if not self.ui.document then
		logger.warn("Crossbill: Cannot sync - no document available")
		return
	end

	if not is_autosync then
		UI.showSyncingMessage()
	end

	local success, err = pcall(function()
		self:doSync(is_autosync)
	end)

	if not success then
		logger.err("Crossbill: Error in sync:", err)
		if not is_autosync then
			UI.showSyncError(err)
		end
	end

	-- Always clean up WiFi after sync
	Network.disableWifiIfNeeded()
end

--- Execute the sync workflow
-- @param is_autosync boolean If true, run in silent mode
function CrossbillSync:doSync(is_autosync)
	-- Extract book metadata
	local book_metadata = BookMetadata:new(self.ui)
	local book_data = book_metadata:extractBookData()
	local doc_path = book_metadata:getDocPath()

	-- Extract highlights
	local highlight_extractor = HighlightExtractor:new(self.ui)
	local highlights = highlight_extractor:getHighlights(doc_path)

	if not highlights or #highlights == 0 then
		logger.dbg("Crossbill: No highlights to sync")
		return
	end

	logger.dbg("Crossbill: Found", #highlights, "highlights")

	-- Add chapter numbers to highlights
	highlight_extractor:addChapterNumbers(highlights)

	-- Upload highlights to server
	local upload_success, response, err = self.api_client:uploadHighlights(book_data, highlights)

	if not upload_success then
		if not is_autosync then
			if err and err:match("^Authentication") then
				UI.showAuthError(err)
			else
				UI.showSyncFailed(err)
			end
		end
		return
	end

	-- Upload cover image if available
	if response and response.book_id then
		self:uploadCoverImage(response.book_id, book_metadata)
	end

	-- Show success message for manual syncs
	if not is_autosync then
		UI.showSyncSuccess(response.highlights_created, response.highlights_skipped)
	end
end

--- Upload cover image for a book
-- @param book_id number The book ID from the server
-- @param book_metadata BookMetadata instance
function CrossbillSync:uploadCoverImage(book_id, book_metadata)
	local success, err = pcall(function()
		local tmp_path, cover_data, cover_image = book_metadata:extractCoverToFile(book_id)

		if not cover_data then
			return
		end

		-- Upload cover
		self.api_client:uploadCover(book_id, cover_data)

		-- Cleanup
		if cover_image then
			cover_image:free()
		end
		if tmp_path then
			os.remove(tmp_path)
		end
	end)

	if not success then
		logger.err("Crossbill: Error uploading cover:", err)
	end
end

-- Event handlers for auto-sync

--- Called when document is closed
function CrossbillSync:onCloseDocument()
	-- Don't auto-sync on document close to avoid nil document errors
	return false
end

--- Called when device goes to sleep/suspend
function CrossbillSync:onSuspend()
	if self.settings:isAutosyncEnabled() then
		logger.info("Crossbill: Auto-syncing on suspend")
		self:syncCurrentBook(true)
	end
	return false
end

--- Called when KOReader exits
function CrossbillSync:onExit()
	if self.settings:isAutosyncEnabled() then
		logger.info("Crossbill: Auto-syncing on exit")
		self:syncCurrentBook(true)
	end
	return false
end

return CrossbillSync
