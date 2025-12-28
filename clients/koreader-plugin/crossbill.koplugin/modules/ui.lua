--[[
UI Module for Crossbill Sync

Provides UI components for the plugin including:
- Information messages and notifications
- Server configuration dialog
- Menu structure
]]

local UIManager = require("ui/uimanager")
local InfoMessage = require("ui/widget/infomessage")
local MultiInputDialog = require("ui/widget/multiinputdialog")
local _ = require("gettext")

local UI = {}

--- Show an informational message to the user
-- @param text string The message to display
-- @param timeout number|nil Auto-dismiss timeout in seconds (nil = no auto-dismiss)
function UI.showMessage(text, timeout)
	UIManager:show(InfoMessage:new({
		text = text,
		timeout = timeout,
	}))
end

--- Show a syncing in progress message
function UI.showSyncingMessage()
	UI.showMessage(_("Syncing highlights..."), 2)
end

--- Show sync success message
-- @param created number Number of new highlights
-- @param skipped number Number of duplicate highlights
function UI.showSyncSuccess(created, skipped)
	UI.showMessage(string.format(_("Synced successfully!\n%d new, %d duplicates"), created or 0, skipped or 0), 3)
end

--- Show sync error message
-- @param error_msg string The error message
function UI.showSyncError(error_msg)
	UI.showMessage(_("Sync error: ") .. tostring(error_msg), 5)
end

--- Show sync failed message
-- @param code number|string The error code
function UI.showSyncFailed(code)
	UI.showMessage(_("Sync failed: ") .. tostring(code or "unknown error"), 3)
end

--- Show authentication error message
-- @param error_msg string The error message
function UI.showAuthError(error_msg)
	UI.showMessage(_("Authentication failed: ") .. (error_msg or "unknown error"), 5)
end

--- Show settings saved message
function UI.showSettingsSaved()
	UI.showMessage(_("Settings saved"))
end

--- Show autosync status change message
-- @param enabled boolean Whether autosync is now enabled
function UI.showAutosyncToggled(enabled)
	UI.showMessage(enabled and _("Auto-sync enabled") or _("Auto-sync disabled"))
end

--- Show server configuration dialog
-- @param settings Settings instance
-- @param on_save function Callback when settings are saved
function UI.showConfigureServerDialog(settings, on_save)
	local dialog
	dialog = MultiInputDialog:new({
		title = _("Crossbill Settings"),
		fields = {
			{
				text = settings:getBaseUrl() or "",
				hint = _("Server URL (e.g., https://example.com)"),
			},
			{
				text = settings:getUsername() or "",
				hint = _("Username"),
			},
			{
				text = settings:getPassword() or "",
				hint = _("Password"),
				text_type = "password",
			},
		},
		buttons = {
			{
				{
					text = _("Cancel"),
					callback = function()
						UIManager:close(dialog)
					end,
				},
				{
					text = _("Save"),
					is_enter_default = true,
					callback = function()
						local fields = dialog:getFields()
						local base_url = fields[1]
						local username = fields[2]
						local password = fields[3]

						settings:updateServerConfig(base_url, username, password)
						UIManager:close(dialog)
						UI.showSettingsSaved()

						if on_save then
							on_save()
						end
					end,
				},
			},
		},
	})

	UIManager:show(dialog)
	dialog:onShowKeyboard()
end

--- Build the main menu structure for the plugin
-- @param handlers table Callback handlers for menu actions
--   - on_sync: function() Called when sync is triggered
--   - on_configure: function() Called when configure is triggered
--   - is_autosync_enabled: function() Returns autosync state
--   - on_toggle_autosync: function() Called when autosync is toggled
-- @return table Menu item table for KOReader
function UI.buildMenuItems(handlers)
	return {
		text = _("Crossbill Sync"),
		sorting_hint = "tools",
		sub_item_table = {
			{
				text = _("Sync Current Book"),
				callback = handlers.on_sync,
			},
			{
				text = _("Configure Server"),
				callback = handlers.on_configure,
			},
			{
				text = _("Auto-sync"),
				checked_func = handlers.is_autosync_enabled,
				callback = handlers.on_toggle_autosync,
			},
		},
	}
end

return UI
