/**
 * API client for communicating with Crossbill backend
 */

import { BooksListResponse, BookDetails } from './types';

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export class CrossbillAPI {
  private bearerToken: string = '';
  private email: string = '';
  private password: string = '';
  private onTokenUpdate?: (token: string) => Promise<void>;

  constructor(
    private serverHost: string,
    bearerToken?: string,
    email?: string,
    password?: string
  ) {
    if (bearerToken) {
      this.bearerToken = bearerToken;
    }
    if (email) {
      this.email = email;
    }
    if (password) {
      this.password = password;
    }
  }

  setCredentials(email: string, password: string) {
    this.email = email;
    this.password = password;
  }

  setBearerToken(token: string) {
    this.bearerToken = token;
  }

  setOnTokenUpdate(callback: (token: string) => Promise<void>) {
    this.onTokenUpdate = callback;
  }

  private async ensureAuthenticated(): Promise<void> {
    if (this.bearerToken) {
      return;
    }

    if (!this.email || !this.password) {
      throw new Error('No credentials provided. Please set email and password in settings.');
    }

    await this.login(this.email, this.password);
  }

  async login(email: string, password: string): Promise<LoginResponse> {
    const formData = new URLSearchParams();
    formData.append('username', email); // Backend uses 'username' field for email
    formData.append('password', password);

    const response = await fetch(`${this.serverHost}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Login failed (${response.status}): ${errorText || response.statusText}`);
    }

    const data: LoginResponse = await response.json();
    this.bearerToken = data.access_token;

    // Notify the plugin to save the token
    if (this.onTokenUpdate) {
      await this.onTokenUpdate(data.access_token);
    }

    return data;
  }

  private getAuthHeaders(): HeadersInit {
    if (this.bearerToken) {
      return {
        'Authorization': `Bearer ${this.bearerToken}`,
      };
    }
    return {};
  }

  private async authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
    await this.ensureAuthenticated();

    const headers = {
      ...options.headers,
      ...this.getAuthHeaders(),
    };

    const response = await fetch(url, { ...options, headers });

    if (response.status === 401) {
      this.bearerToken = '';
      await this.ensureAuthenticated();

      const retryHeaders = {
        ...options.headers,
        ...this.getAuthHeaders(),
      };
      return await fetch(url, { ...options, headers: retryHeaders });
    }

    return response;
  }

  async getBooks(): Promise<BooksListResponse> {
    const response = await this.authenticatedFetch(
      `${this.serverHost}/api/v1/highlights/books?limit=1000`
    );
    if (!response.ok) {
      throw new Error(`Failed to fetch books: ${response.statusText}`);
    }
    return await response.json();
  }

  async getBookDetails(bookId: number): Promise<BookDetails> {
    const response = await this.authenticatedFetch(`${this.serverHost}/api/v1/book/${bookId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch book details: ${response.statusText}`);
    }
    return await response.json();
  }
}
