--[[
Network Module for Crossbill Sync

Provides HTTP/HTTPS request utilities and WiFi management.
Abstracts away the complexity of KOReader's networking layer.
]]

local socket = require("socket")
local http = require("socket.http")
local https = require("ssl.https")
local ltn12 = require("ltn12")
local socketutil = require("socketutil")
local NetworkMgr = require("ui/network/manager")
local logger = require("logger")

local Network = {}

-- Track whether we enabled WiFi (so we can turn it off after sync)
local wifi_enabled_by_us = false

--- URL encode a string for use in form-urlencoded data
-- @param str string The string to encode
-- @return string The URL-encoded string
function Network.urlEncode(str)
	if str then
		str = string.gsub(str, "\n", "\r\n")
		str = string.gsub(str, "([^%w _%%%-%.~])", function(c)
			return string.format("%%%02X", string.byte(c))
		end)
		str = string.gsub(str, " ", "+")
	end
	return str
end

--- Make an HTTP/HTTPS request
-- @param options table Request options
--   - url: string (required) The URL to request
--   - method: string (default "GET") HTTP method
--   - headers: table HTTP headers
--   - body: string Request body
-- @return number|nil HTTP status code
-- @return string Response body
-- @return string|nil Error message
function Network.request(options)
	local url = options.url
	local method = options.method or "GET"
	local headers = options.headers or {}
	local body = options.body

	-- Set content length header if body is provided
	if body and not headers["Content-Length"] then
		headers["Content-Length"] = tostring(#body)
	end

	local response_body = {}
	local request = {
		url = url,
		method = method,
		headers = headers,
		sink = ltn12.sink.table(response_body),
	}

	if body then
		request.source = ltn12.source.string(body)
	end

	-- Use HTTP or HTTPS based on URL scheme
	local code, status_or_err
	if url:match("^https://") then
		logger.dbg("Crossbill Network: Using HTTPS for", url)
		code, status_or_err = socket.skip(1, https.request(request))
	else
		logger.dbg("Crossbill Network: Using HTTP for", url)
		code, status_or_err = socket.skip(1, http.request(request))
	end

	-- Reset socket timeout
	socketutil:reset_timeout()

	local response_text = table.concat(response_body)
	logger.dbg("Crossbill Network: Response code:", code)

	if code then
		return code, response_text, nil
	else
		return nil, "", status_or_err or "Unknown network error"
	end
end

--- Make a JSON POST request
-- @param url string The URL to request
-- @param data table The data to JSON-encode and send
-- @param token string|nil Bearer token for authorization
-- @return number|nil HTTP status code
-- @return table|nil Parsed JSON response
-- @return string|nil Error message
function Network.postJson(url, data, token)
	local JSON = require("json")
	local body = JSON.encode(data)

	local headers = {
		["Content-Type"] = "application/json",
		["Accept"] = "application/json",
	}

	if token then
		headers["Authorization"] = "Bearer " .. token
	end

	local code, response_text, err = Network.request({
		url = url,
		method = "POST",
		headers = headers,
		body = body,
	})

	if not code then
		return nil, nil, err
	end

	if response_text and response_text ~= "" then
		local ok, response_data = pcall(JSON.decode, response_text)
		if ok then
			return code, response_data, nil
		else
			return code, nil, "Invalid JSON response"
		end
	end

	return code, nil, nil
end

--- Make a form-urlencoded POST request
-- @param url string The URL to request
-- @param data table Key-value pairs to encode
-- @return number|nil HTTP status code
-- @return table|nil Parsed JSON response
-- @return string|nil Error message
function Network.postForm(url, data)
	local JSON = require("json")

	-- Build form-urlencoded body
	local parts = {}
	for key, value in pairs(data) do
		table.insert(parts, Network.urlEncode(key) .. "=" .. Network.urlEncode(value))
	end
	local body = table.concat(parts, "&")

	local headers = {
		["Content-Type"] = "application/x-www-form-urlencoded",
		["Accept"] = "application/json",
	}

	local code, response_text, err = Network.request({
		url = url,
		method = "POST",
		headers = headers,
		body = body,
	})

	if not code then
		return nil, nil, err
	end

	if response_text and response_text ~= "" then
		local ok, response_data = pcall(JSON.decode, response_text)
		if ok then
			return code, response_data, nil
		else
			return code, nil, "Invalid JSON response"
		end
	end

	return code, nil, nil
end

--- Make a multipart/form-data POST request
-- @param url string The URL to request
-- @param files table Array of file objects {name, filename, content_type, data}
-- @param token string|nil Bearer token for authorization
-- @return number|nil HTTP status code
-- @return string Response body
-- @return string|nil Error message
function Network.postMultipart(url, files, token)
	local boundary = "----CrossbillBoundary" .. os.time()
	local body_parts = {}

	for _, file in ipairs(files) do
		table.insert(body_parts, "--" .. boundary)
		table.insert(
			body_parts,
			string.format('Content-Disposition: form-data; name="%s"; filename="%s"', file.name, file.filename)
		)
		table.insert(body_parts, "Content-Type: " .. file.content_type)
		table.insert(body_parts, "")
		table.insert(body_parts, file.data)
	end
	table.insert(body_parts, "--" .. boundary .. "--")

	local body = table.concat(body_parts, "\r\n")

	local headers = {
		["Content-Type"] = "multipart/form-data; boundary=" .. boundary,
	}

	if token then
		headers["Authorization"] = "Bearer " .. token
	end

	return Network.request({
		url = url,
		method = "POST",
		headers = headers,
		body = body,
	})
end

--- Ensure WiFi is enabled, calling callback when ready
-- @param callback function Function to call when network is available
-- @return boolean True if already online, false if waiting for connection
function Network.ensureWifiEnabled(callback)
	if NetworkMgr:willRerunWhenOnline(callback) then
		-- Network is off, NetworkMgr will call callback when online
		logger.info("Crossbill Network: WiFi is off, prompting to enable...")
		wifi_enabled_by_us = true
		return false
	else
		-- Network is already on
		logger.info("Crossbill Network: WiFi already enabled")
		wifi_enabled_by_us = false
		return true
	end
end

--- Disable WiFi if we enabled it for the sync
function Network.disableWifiIfNeeded()
	if wifi_enabled_by_us then
		logger.info("Crossbill Network: Disabling WiFi after sync")
		NetworkMgr:turnOffWifi()
		wifi_enabled_by_us = false
	else
		logger.info("Crossbill Network: WiFi was already on, leaving it enabled")
	end
end

--- Check if we enabled WiFi
-- @return boolean True if we enabled WiFi
function Network.didWeEnableWifi()
	return wifi_enabled_by_us
end

return Network
