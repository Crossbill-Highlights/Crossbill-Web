/**
 * Modal dialogs for book, chapter, and highlight selection
 */

import { App, SuggestModal } from 'obsidian';
import { BookWithHighlightCount, ChapterWithHighlights, HighlightWithChapterInfo } from './types';

/**
 * Modal for selecting a book from the user's library
 */
export class BookSuggestModal extends SuggestModal<BookWithHighlightCount> {
  private books: BookWithHighlightCount[];
  private onSelect: (book: BookWithHighlightCount) => void;

  constructor(
    app: App,
    books: BookWithHighlightCount[],
    onSelect: (book: BookWithHighlightCount) => void
  ) {
    super(app);
    this.books = books;
    this.onSelect = onSelect;
    this.setPlaceholder('Select a book...');
  }

  getSuggestions(query: string): BookWithHighlightCount[] {
    const lowerQuery = query.toLowerCase();
    return this.books.filter((book) => {
      const title = book.title.toLowerCase();
      const author = book.author?.toLowerCase() || '';
      return title.includes(lowerQuery) || author.includes(lowerQuery);
    });
  }

  renderSuggestion(book: BookWithHighlightCount, el: HTMLElement) {
    el.createEl('div', { text: book.title, cls: 'crossbill-book-title' });
    if (book.author) {
      el.createEl('small', { text: book.author, cls: 'crossbill-book-author' });
    }
    el.createEl('small', {
      text: ` (${book.highlight_count} highlights)`,
      cls: 'crossbill-highlight-count',
    });
  }

  onChooseSuggestion(book: BookWithHighlightCount) {
    this.onSelect(book);
  }
}

/**
 * Modal for selecting a chapter from a book
 */
export class ChapterSuggestModal extends SuggestModal<ChapterWithHighlights> {
  private chapters: ChapterWithHighlights[];
  private onSelect: (chapter: ChapterWithHighlights) => void;

  constructor(
    app: App,
    chapters: ChapterWithHighlights[],
    onSelect: (chapter: ChapterWithHighlights) => void
  ) {
    super(app);
    this.chapters = chapters;
    this.onSelect = onSelect;
    this.setPlaceholder('Select a chapter...');
  }

  getSuggestions(query: string): ChapterWithHighlights[] {
    const lowerQuery = query.toLowerCase();
    return this.chapters.filter((chapter) => chapter.name.toLowerCase().includes(lowerQuery));
  }

  renderSuggestion(chapter: ChapterWithHighlights, el: HTMLElement) {
    el.createEl('div', { text: chapter.name, cls: 'crossbill-chapter-name' });
    el.createEl('small', {
      text: ` (${chapter.highlights.length} highlights)`,
      cls: 'crossbill-highlight-count',
    });
  }

  onChooseSuggestion(chapter: ChapterWithHighlights) {
    this.onSelect(chapter);
  }
}

/**
 * Modal for selecting a single highlight from all chapters
 */
export class HighlightSuggestModal extends SuggestModal<HighlightWithChapterInfo> {
  private highlights: HighlightWithChapterInfo[];
  private onSelect: (highlight: HighlightWithChapterInfo) => void;

  constructor(
    app: App,
    highlights: HighlightWithChapterInfo[],
    onSelect: (highlight: HighlightWithChapterInfo) => void
  ) {
    super(app);
    this.highlights = highlights;
    this.onSelect = onSelect;
    this.setPlaceholder('Search highlights...');
  }

  getSuggestions(query: string): HighlightWithChapterInfo[] {
    const lowerQuery = query.toLowerCase();
    return this.highlights.filter((highlight) => {
      const text = highlight.text.toLowerCase();
      const chapter = highlight.chapterName.toLowerCase();
      const note = highlight.note?.toLowerCase() || '';
      return text.includes(lowerQuery) || chapter.includes(lowerQuery) || note.includes(lowerQuery);
    });
  }

  renderSuggestion(highlight: HighlightWithChapterInfo, el: HTMLElement) {
    // Truncate highlight text if too long
    const maxLength = 80;
    const truncatedText =
      highlight.text.length > maxLength
        ? highlight.text.substring(0, maxLength) + '...'
        : highlight.text;

    el.createEl('div', { text: truncatedText, cls: 'crossbill-highlight-text' });

    // Show chapter and page info
    let metadata = highlight.chapterName;
    if (highlight.page !== null) {
      metadata += ` • Page ${highlight.page}`;
    }
    el.createEl('small', { text: metadata, cls: 'crossbill-highlight-metadata' });
  }

  onChooseSuggestion(highlight: HighlightWithChapterInfo) {
    this.onSelect(highlight);
  }
}
