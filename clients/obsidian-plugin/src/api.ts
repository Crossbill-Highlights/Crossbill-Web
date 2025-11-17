/**
 * API client for communicating with Crossbill backend
 */

import { BooksListResponse, BookDetails } from './types';

export class CrossbillAPI {
  constructor(private serverHost: string) {}

  async getBooks(): Promise<BooksListResponse> {
    const response = await fetch(`${this.serverHost}/api/v1/highlights/books?limit=1000`);
    if (!response.ok) {
      throw new Error(`Failed to fetch books: ${response.statusText}`);
    }
    return await response.json();
  }

  async getBookDetails(bookId: number): Promise<BookDetails> {
    const response = await fetch(`${this.serverHost}/api/v1/book/${bookId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch book details: ${response.statusText}`);
    }
    return await response.json();
  }
}
