--[[
API Client Module for Crossbill Sync

Provides a clean interface for communicating with the Crossbill server API.
Handles highlight uploads, cover image uploads, and other API operations.
]]

local Network = require("modules/network")
local logger = require("logger")

local ApiClient = {}
ApiClient.__index = ApiClient

--- Create a new ApiClient instance
-- @param settings Settings instance
-- @param auth Auth instance
-- @return ApiClient instance
function ApiClient:new(settings, auth)
	local instance = setmetatable({}, ApiClient)
	instance.settings = settings
	instance.auth = auth
	return instance
end

--- Get the API base URL
-- @return string API base URL
function ApiClient:getApiUrl()
	return self.settings:getBaseUrl() .. "/api/v1"
end

--- Upload highlights to the server
-- @param book_data table Book metadata
-- @param highlights table Array of highlights
-- @return boolean Success status
-- @return table|nil Response data containing book_id, highlights_created, highlights_skipped
-- @return string|nil Error message
function ApiClient:uploadHighlights(book_data, highlights)
	local token, auth_err = self.auth:getValidToken()
	if not token then
		return false, nil, auth_err or "Authentication failed"
	end

	local payload = {
		book = book_data,
		highlights = highlights,
	}

	local api_url = self:getApiUrl() .. "/highlights/upload"
	logger.dbg("Crossbill API: Sending highlights to", api_url)

	local code, response_data, err = Network.postJson(api_url, payload, token)

	if not code then
		logger.err("Crossbill API: Network error:", err)
		return false, nil, err or "Network error"
	end

	if code == 200 and response_data then
		logger.dbg("Crossbill API: Highlights uploaded successfully")
		return true, response_data, nil
	else
		logger.err("Crossbill API: Upload failed with code:", code)
		return false, nil, "Upload failed: " .. tostring(code)
	end
end

--- Upload a cover image for a book
-- @param book_id number The book ID
-- @param cover_data string The cover image binary data
-- @return boolean Success status
-- @return string|nil Error message
function ApiClient:uploadCover(book_id, cover_data)
	local token, auth_err = self.auth:getValidToken()
	if not token then
		return false, auth_err or "Authentication failed"
	end

	local api_url = self:getApiUrl() .. "/books/" .. book_id .. "/metadata/cover"
	logger.dbg("Crossbill API: Uploading cover to", api_url)

	local files = {
		{
			name = "cover",
			filename = "cover.jpg",
			content_type = "image/jpeg",
			data = cover_data,
		},
	}

	local code, _, err = Network.postMultipart(api_url, files, token)

	if not code then
		logger.err("Crossbill API: Network error uploading cover:", err)
		return false, err or "Network error"
	end

	if code == 200 then
		logger.info("Crossbill API: Cover uploaded successfully for book", book_id)
		return true, nil
	else
		logger.warn("Crossbill API: Cover upload failed with code:", code)
		return false, "Upload failed: " .. tostring(code)
	end
end

return ApiClient
