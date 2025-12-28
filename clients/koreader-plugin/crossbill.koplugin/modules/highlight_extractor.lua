--[[
Highlight Extractor Module for Crossbill Sync

Extracts highlights from KOReader documents.
Supports both modern annotations format and legacy highlight format.
Also handles chapter number mapping from table of contents.
]]

local DocSettings = require("docsettings")
local logger = require("logger")

local HighlightExtractor = {}
HighlightExtractor.__index = HighlightExtractor

--- Create a new HighlightExtractor instance
-- @param ui table The KOReader UI context (self.ui from plugin)
-- @return HighlightExtractor instance
function HighlightExtractor:new(ui)
	local instance = setmetatable({}, HighlightExtractor)
	instance.ui = ui
	return instance
end

--- Convert a raw annotation to our standard highlight format
-- @param annotation table The raw annotation object
-- @return table Formatted highlight object
local function formatHighlight(annotation)
	return {
		text = annotation.text or "",
		note = annotation.note or nil,
		datetime = annotation.datetime or "",
		page = annotation.pageno or annotation.page,
		chapter = annotation.chapter or nil,
	}
end

--- Get highlights directly from ReaderAnnotation's memory
-- This is preferred as it captures annotations not yet flushed to disk
-- @return table|nil Array of highlights, or nil if not available
function HighlightExtractor:getHighlightsFromMemory()
	if not self.ui.annotation then
		logger.dbg("Crossbill Extractor: ReaderAnnotation module not available")
		return nil
	end

	local annotations = self.ui.annotation.annotations
	if not annotations or #annotations == 0 then
		logger.dbg("Crossbill Extractor: No annotations in memory")
		return nil
	end

	logger.dbg("Crossbill Extractor: Found", #annotations, "annotations in memory")
	local results = {}

	for _, annotation in ipairs(annotations) do
		-- Only include highlights and notes, skip other annotation types
		if annotation.text or annotation.note then
			table.insert(results, formatHighlight(annotation))
		end
	end

	logger.dbg("Crossbill Extractor: Converted", #results, "annotations to highlights")
	return results
end

--- Get highlights from document settings file (disk)
-- Supports both modern annotations format and legacy highlight format
-- @param doc_path string Path to the document
-- @return table|nil Array of highlights, or nil if none found
function HighlightExtractor:getHighlightsFromDisk(doc_path)
	local doc_settings = DocSettings:open(doc_path)
	local results = {}

	-- Try modern annotations format first
	local annotations = doc_settings:readSetting("annotations")
	if annotations then
		for _, annotation in ipairs(annotations) do
			table.insert(results, formatHighlight(annotation))
		end
		logger.dbg("Crossbill Extractor: Found", #results, "highlights in modern format")
		return results
	end

	-- Fallback to legacy highlight format
	local highlights = doc_settings:readSetting("highlight")
	if not highlights then
		logger.dbg("Crossbill Extractor: No highlights found in settings")
		return nil
	end

	local bookmarks = doc_settings:readSetting("bookmarks") or {}

	for _, items in pairs(highlights) do
		for _, item in ipairs(items) do
			local note = nil

			-- Find matching bookmark for note (in legacy format, notes are in bookmarks)
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

	logger.dbg("Crossbill Extractor: Found", #results, "highlights in legacy format")
	return results
end

--- Get all highlights, trying memory first then falling back to disk
-- @param doc_path string Path to the document
-- @return table|nil Array of highlights
function HighlightExtractor:getHighlights(doc_path)
	return self:getHighlightsFromMemory() or self:getHighlightsFromDisk(doc_path)
end

--- Get chapter number mapping from table of contents
-- Maps chapter names to their order number for proper sorting
-- @return table Map of chapter name -> chapter number
function HighlightExtractor:getChapterNumberMap()
	local chapter_map = {}

	-- Get TOC from the document
	if self.ui.toc and self.ui.toc.toc then
		local toc = self.ui.toc.toc

		for i, item in ipairs(toc) do
			if item.title then
				chapter_map[item.title] = i
			end
		end

		logger.dbg("Crossbill Extractor: Created mapping for", #toc, "chapters from TOC")
	else
		logger.dbg("Crossbill Extractor: No TOC available for this document")
	end

	return chapter_map
end

--- Add chapter numbers to highlights based on chapter names
-- @param highlights table Array of highlights to augment
-- @return table The same highlights array with chapter_number added
function HighlightExtractor:addChapterNumbers(highlights)
	local chapter_map = self:getChapterNumberMap()

	for _, highlight in ipairs(highlights) do
		if highlight.chapter and chapter_map[highlight.chapter] then
			highlight.chapter_number = chapter_map[highlight.chapter]
		end
	end

	return highlights
end

return HighlightExtractor
