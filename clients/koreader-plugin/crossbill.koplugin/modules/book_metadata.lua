--[[
Book Metadata Module for Crossbill Sync

Extracts book metadata from KOReader documents including:
- Title, author, description
- ISBN from identifiers
- Language, page count
- Keywords/tags
- Cover image
]]

local DocSettings = require("docsettings")
local FileManagerBookInfo = require("apps/filemanager/filemanagerbookinfo")
local logger = require("logger")

local BookMetadata = {}
BookMetadata.__index = BookMetadata

--- Create a new BookMetadata instance
-- @param ui table The KOReader UI context (self.ui from plugin)
-- @return BookMetadata instance
function BookMetadata:new(ui)
	local instance = setmetatable({}, BookMetadata)
	instance.ui = ui
	return instance
end

--- Extract filename from a file path
-- @param path string Full file path
-- @return string Filename only
local function getFilename(path)
	return path:match("^.+/(.+)$") or path
end

--- Extract ISBN from identifiers string
-- The format can vary: "ISBN:9780735211292\nAMAZON:..." or "ISBN:9780735211292 AMAZON:..."
-- @param identifiers string The identifiers string
-- @return string|nil ISBN if found
local function extractISBN(identifiers)
	if not identifiers then
		return nil
	end

	-- Match ISBN: followed by digits/hyphens/X until we hit a non-ISBN character
	local isbn = identifiers:match("ISBN:([%d%-xX]+)")
	if isbn then
		logger.dbg("Crossbill Metadata: Extracted ISBN:", isbn)
	else
		logger.dbg("Crossbill Metadata: No ISBN found in identifiers:", identifiers)
	end
	return isbn
end

--- Parse keywords string into array
-- Keywords are separated by newlines
-- @param keywords_str string The keywords string
-- @return table|nil Array of keywords
local function parseKeywords(keywords_str)
	if not keywords_str then
		return nil
	end

	local keywords = {}
	for keyword in keywords_str:gmatch("[^\n]+") do
		local trimmed = keyword:match("^%s*(.-)%s*$")
		if trimmed and trimmed ~= "" then
			table.insert(keywords, trimmed)
		end
	end

	if #keywords > 0 then
		logger.dbg("Crossbill Metadata: Extracted", #keywords, "keywords")
		return keywords
	end
	return nil
end

--- Get document settings for metadata
-- @param doc_path string Path to the document
-- @return table Combined metadata from doc_props and doc_settings
function BookMetadata:getDocMetadata(doc_path)
	local doc_settings = DocSettings:open(doc_path)
	local book_props = self.ui.doc_props

	-- Merge doc_settings metadata with live doc_props
	local metadata_props = doc_settings:readSetting("doc_props") or book_props

	return {
		book_props = book_props,
		metadata_props = metadata_props,
		doc_settings = doc_settings,
	}
end

--- Extract complete book metadata
-- @return table Book data ready for API upload
function BookMetadata:extractBookData()
	local doc_path = self.ui.document.file
	local meta = self:getDocMetadata(doc_path)

	local book_props = meta.book_props
	local metadata_props = meta.metadata_props
	local doc_settings = meta.doc_settings

	-- Extract ISBN from identifiers
	local isbn = extractISBN(metadata_props.identifiers)

	-- Extract language
	local language = metadata_props.language or nil
	if language then
		logger.dbg("Crossbill Metadata: Extracted language:", language)
	end

	-- Extract page count
	local page_count = doc_settings:readSetting("doc_pages") or nil
	if page_count then
		logger.dbg("Crossbill Metadata: Extracted page count:", page_count)
	end

	-- Parse keywords into array
	local keywords = parseKeywords(metadata_props.keywords)

	-- Build book data
	local title = book_props.display_title or book_props.title or getFilename(doc_path)
	logger.dbg("Crossbill Metadata: Syncing book:", title)

	return {
		title = title,
		author = book_props.authors or nil,
		isbn = isbn,
		description = metadata_props.description or nil,
		language = language,
		page_count = page_count,
		keywords = keywords,
	}
end

--- Extract cover image from document
-- @return userdata|nil Cover image object (must be freed after use)
function BookMetadata:extractCover()
	if not self.ui.document then
		logger.dbg("Crossbill Metadata: No document available for cover extraction")
		return nil
	end

	local cover_image = FileManagerBookInfo:getCoverImage(self.ui.document)
	if cover_image then
		logger.dbg(
			"Crossbill Metadata: Cover image extracted, size:",
			cover_image:getWidth(),
			"x",
			cover_image:getHeight()
		)
	else
		logger.dbg("Crossbill Metadata: No cover image available for this document")
	end

	return cover_image
end

--- Save cover image to temporary file and return path and data
-- Caller is responsible for cleaning up the temp file and freeing the image
-- @return string|nil Temporary file path
-- @return string|nil Cover image data
-- @return userdata|nil Cover image object (caller must free)
function BookMetadata:extractCoverToFile(book_id)
	local cover_image = self:extractCover()
	if not cover_image then
		return nil, nil, nil
	end

	local tmp_path = "/tmp/crossbill_cover_" .. book_id .. ".jpg"
	cover_image:writeToFile(tmp_path)
	logger.dbg("Crossbill Metadata: Cover saved to temporary file:", tmp_path)

	-- Read the file content
	local cover_file = io.open(tmp_path, "rb")
	if not cover_file then
		logger.err("Crossbill Metadata: Failed to open temporary cover file")
		cover_image:free()
		return nil, nil, nil
	end

	local cover_data = cover_file:read("*all")
	cover_file:close()

	return tmp_path, cover_data, cover_image
end

--- Get document path
-- @return string Document file path
function BookMetadata:getDocPath()
	return self.ui.document.file
end

--- Check if document is available
-- @return boolean True if document is loaded
function BookMetadata:hasDocument()
	return self.ui.document ~= nil
end

return BookMetadata
