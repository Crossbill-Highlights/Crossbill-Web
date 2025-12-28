--[[
Settings Module for Crossbill Sync

Manages plugin configuration including server URL, credentials, and tokens.
Provides a clean API for loading, saving, and accessing settings.
]]

local logger = require("logger")

local Settings = {}
Settings.__index = Settings

-- Default settings values
local DEFAULTS = {
	base_url = "http://localhost:8000",
	username = "",
	password = "",
	autosync_enabled = false,
	access_token = nil,
	refresh_token = nil,
	token_expires_at = nil,
}

-- Settings key in KOReader's global settings
local SETTINGS_KEY = "crossbill_sync"

--- Create a new Settings instance
-- @return Settings instance
function Settings:new()
	local instance = setmetatable({}, Settings)
	instance._data = nil
	return instance
end

--- Load settings from KOReader's global settings
-- @return self for chaining
function Settings:load()
	self._data = G_reader_settings:readSetting(SETTINGS_KEY) or {}
	-- Apply defaults for any missing keys
	for key, value in pairs(DEFAULTS) do
		if self._data[key] == nil then
			self._data[key] = value
		end
	end
	logger.dbg("Crossbill Settings: Loaded settings")
	return self
end

--- Save settings to KOReader's global settings
-- @return self for chaining
function Settings:save()
	G_reader_settings:saveSetting(SETTINGS_KEY, self._data)
	logger.dbg("Crossbill Settings: Saved settings")
	return self
end

--- Get a setting value
-- @param key string The setting key
-- @return mixed The setting value
function Settings:get(key)
	if self._data == nil then
		self:load()
	end
	return self._data[key]
end

--- Set a setting value
-- @param key string The setting key
-- @param value mixed The setting value
-- @return self for chaining
function Settings:set(key, value)
	if self._data == nil then
		self:load()
	end
	self._data[key] = value
	return self
end

--- Get the base URL
-- @return string The server base URL
function Settings:getBaseUrl()
	return self:get("base_url")
end

--- Set the base URL (normalizes by removing trailing slash)
-- @param url string The server base URL
-- @return self for chaining
function Settings:setBaseUrl(url)
	-- Remove trailing slash if present
	local normalized = url:gsub("/$", "")
	return self:set("base_url", normalized)
end

--- Get the username
-- @return string The username
function Settings:getUsername()
	return self:get("username") or ""
end

--- Set the username
-- @param username string The username
-- @return self for chaining
function Settings:setUsername(username)
	return self:set("username", username)
end

--- Get the password
-- @return string The password
function Settings:getPassword()
	return self:get("password") or ""
end

--- Set the password
-- @param password string The password
-- @return self for chaining
function Settings:setPassword(password)
	return self:set("password", password)
end

--- Check if autosync is enabled
-- @return boolean True if autosync is enabled
function Settings:isAutosyncEnabled()
	return self:get("autosync_enabled") == true
end

--- Toggle autosync setting
-- @return boolean The new autosync state
function Settings:toggleAutosync()
	local new_state = not self:isAutosyncEnabled()
	self:set("autosync_enabled", new_state)
	self:save()
	return new_state
end

--- Get the cached access token
-- @return string|nil The access token
function Settings:getAccessToken()
	return self:get("access_token")
end

--- Get the cached refresh token
-- @return string|nil The refresh token
function Settings:getRefreshToken()
	return self:get("refresh_token")
end

--- Get the token expiration timestamp
-- @return number|nil Unix timestamp when token expires
function Settings:getTokenExpiresAt()
	return self:get("token_expires_at")
end

--- Store authentication tokens
-- @param access_token string The access token
-- @param refresh_token string|nil The refresh token
-- @param expires_in number|nil Seconds until token expires
-- @return self for chaining
function Settings:setTokens(access_token, refresh_token, expires_in)
	self:set("access_token", access_token)
	if refresh_token then
		self:set("refresh_token", refresh_token)
	end
	if expires_in then
		self:set("token_expires_at", os.time() + expires_in)
	end
	return self:save()
end

--- Clear all authentication tokens
-- @return self for chaining
function Settings:clearTokens()
	self:set("access_token", nil)
	self:set("refresh_token", nil)
	self:set("token_expires_at", nil)
	return self:save()
end

--- Check if credentials are configured
-- @return boolean True if username and password are set
function Settings:hasCredentials()
	local username = self:getUsername()
	local password = self:getPassword()
	return username ~= "" and password ~= ""
end

--- Update server configuration
-- @param base_url string The server URL
-- @param username string The username
-- @param password string The password
-- @return self for chaining
function Settings:updateServerConfig(base_url, username, password)
	self:setBaseUrl(base_url)
	self:setUsername(username)
	self:setPassword(password)
	return self:save()
end

return Settings
