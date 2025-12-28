--[[
Authentication Module for Crossbill Sync

Handles user authentication with the Crossbill server including:
- Initial login with username/password
- Token refresh using refresh tokens
- Token validation and caching
]]

local Network = require("modules/network")
local logger = require("logger")

local Auth = {}
Auth.__index = Auth

-- Buffer time before token expiry (in seconds) to trigger refresh
local TOKEN_EXPIRY_BUFFER = 60

--- Create a new Auth instance
-- @param settings Settings instance
-- @return Auth instance
function Auth:new(settings)
	local instance = setmetatable({}, Auth)
	instance.settings = settings
	return instance
end

--- Authenticate with username and password
-- @return string|nil Access token on success
-- @return string|nil Error message on failure
function Auth:login()
	local username = self.settings:getUsername()
	local password = self.settings:getPassword()

	if username == "" or password == "" then
		logger.warn("Crossbill Auth: Username or password not configured")
		return nil, "Username or password not configured"
	end

	local base_url = self.settings:getBaseUrl()
	local api_url = base_url .. "/api/v1/auth/login"
	logger.dbg("Crossbill Auth: Logging in to", api_url)

	local code, response_data, err = Network.postForm(api_url, {
		username = username,
		password = password,
	})

	if not code then
		logger.err("Crossbill Auth: Network error during login:", err)
		return nil, err or "Network error"
	end

	if code == 200 and response_data and response_data.access_token then
		logger.dbg("Crossbill Auth: Login successful")
		self.settings:setTokens(response_data.access_token, response_data.refresh_token, response_data.expires_in)
		return response_data.access_token
	else
		logger.err("Crossbill Auth: Login failed with code:", code)
		return nil, "Login failed: " .. tostring(code)
	end
end

--- Refresh the access token using stored refresh token
-- @return string|nil New access token on success
-- @return string|nil Error message on failure
function Auth:refreshToken()
	local refresh_token = self.settings:getRefreshToken()
	if not refresh_token then
		logger.dbg("Crossbill Auth: No refresh token available")
		return nil, "No refresh token"
	end

	local base_url = self.settings:getBaseUrl()
	local api_url = base_url .. "/api/v1/auth/refresh"
	logger.dbg("Crossbill Auth: Refreshing token at", api_url)

	local code, response_data, err = Network.postJson(api_url, {
		refresh_token = refresh_token,
	})

	if not code then
		logger.err("Crossbill Auth: Network error during refresh:", err)
		return nil, err or "Network error"
	end

	if code == 200 and response_data and response_data.access_token then
		logger.dbg("Crossbill Auth: Token refresh successful")
		self.settings:setTokens(response_data.access_token, response_data.refresh_token, response_data.expires_in)
		return response_data.access_token
	else
		logger.err("Crossbill Auth: Token refresh failed with code:", code)
		-- Clear stored tokens on refresh failure
		self.settings:clearTokens()
		return nil, "Refresh failed: " .. tostring(code)
	end
end

--- Get a valid access token, refreshing or logging in as needed
-- @return string|nil Access token on success
-- @return string|nil Error message on failure
function Auth:getValidToken()
	local current_time = os.time()
	local expires_at = self.settings:getTokenExpiresAt()
	local access_token = self.settings:getAccessToken()

	-- Check if we have a cached token that's still valid (with buffer)
	if access_token and expires_at and (expires_at - TOKEN_EXPIRY_BUFFER) > current_time then
		logger.dbg("Crossbill Auth: Using cached access token")
		return access_token
	end

	-- Try to refresh the token if we have a refresh token
	local refresh_token = self.settings:getRefreshToken()
	if refresh_token then
		logger.dbg("Crossbill Auth: Access token expired or missing, trying refresh")
		local token, err = self:refreshToken()
		if token then
			return token
		end
		logger.dbg("Crossbill Auth: Refresh failed:", err)
	end

	-- Fall back to full login
	logger.dbg("Crossbill Auth: Falling back to full login")
	return self:login()
end

--- Check if authentication is configured
-- @return boolean True if credentials are available
function Auth:isConfigured()
	return self.settings:hasCredentials()
end

return Auth
