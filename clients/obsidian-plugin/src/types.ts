/**
 * Type definitions for Crossbill Obsidian Plugin
 * Based on Crossbill API response schemas
 */

export interface Book {
  id: number;
  title: string;
  author: string | null;
  isbn: string | null;
  created_at: string;
  updated_at: string;
}

export interface BookWithHighlightCount extends Book {
  highlight_count: number;
}

export interface BooksListResponse {
  books: BookWithHighlightCount[];
  total: number;
  offset: number;
  limit: number;
}

export interface HighlightTag {
  id: number;
  name: string;
}

export interface Highlight {
  id: number;
  book_id: number;
  chapter_id: number | null;
  text: string;
  chapter: string | null;
  page: number | null;
  note: string | null;
  datetime: string;
  highlight_tags: HighlightTag[];
  created_at: string;
  updated_at: string;
}

export interface Chapter {
  id: number;
  book_id: number;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface ChapterWithHighlights extends Chapter {
  highlights: Highlight[];
}

export interface BookDetails extends Book {
  chapters: ChapterWithHighlights[];
}

export interface HighlightWithChapterInfo extends Highlight {
  chapterName: string;
}

export interface CrossbillSettings {
  serverHost: string;
}

export const DEFAULT_SETTINGS: CrossbillSettings = {
  serverHost: 'http://localhost:8000',
};
