/**
 * API client for communicating with Crossbill backend
 */

import { BooksListResponse, BookDetails } from './types';

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export class CrossbillAPI {
  private bearerToken: string = '';
  private refreshToken: string = '';
  private tokenExpiresAt: number | null = null;
  private email: string = '';
  private password: string = '';
  private onTokenUpdate?: (token: string, refreshToken: string, expiresAt: number) => Promise<void>;

  constructor(
    private serverHost: string,
    bearerToken?: string,
    email?: string,
    password?: string,
    refreshToken?: string,
    tokenExpiresAt?: number
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
    if (refreshToken) {
      this.refreshToken = refreshToken;
    }
    if (tokenExpiresAt) {
      this.tokenExpiresAt = tokenExpiresAt;
    }
  }

  setCredentials(email: string, password: string) {
    this.email = email;
    this.password = password;
  }

  setBearerToken(token: string, refreshToken?: string, expiresAt?: number) {
    this.bearerToken = token;
    if (refreshToken !== undefined) {
      this.refreshToken = refreshToken;
    }
    if (expiresAt !== undefined) {
      this.tokenExpiresAt = expiresAt;
    }
  }

  setOnTokenUpdate(callback: (token: string, refreshToken: string, expiresAt: number) => Promise<void>) {
    this.onTokenUpdate = callback;
  }

  private isTokenExpired(): boolean {
    if (!this.tokenExpiresAt) {
      return true;
    }
    // Check with 60 second buffer
    return Date.now() > (this.tokenExpiresAt - 60000);
  }

  private async refreshAccessToken(): Promise<boolean> {
    if (!this.refreshToken) {
      return false;
    }

    try {
      const response = await fetch(`${this.serverHost}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: this.refreshToken }),
      });

      if (!response.ok) {
        // Clear tokens on refresh failure
        this.refreshToken = '';
        this.tokenExpiresAt = null;
        return false;
      }

      const data: LoginResponse = await response.json();
      this.bearerToken = data.access_token;
      this.refreshToken = data.refresh_token;
      this.tokenExpiresAt = Date.now() + data.expires_in * 1000;

      // Notify the plugin to save the tokens
      if (this.onTokenUpdate) {
        await this.onTokenUpdate(this.bearerToken, this.refreshToken, this.tokenExpiresAt);
      }

      return true;
    } catch {
      this.refreshToken = '';
      this.tokenExpiresAt = null;
      return false;
    }
  }

  private async ensureAuthenticated(): Promise<void> {
    // Check if we have a valid (non-expired) token
    if (this.bearerToken && !this.isTokenExpired()) {
      return;
    }

    // Try to refresh the token if we have a refresh token
    if (this.refreshToken && await this.refreshAccessToken()) {
      return;
    }

    // Fall back to full login
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
    this.refreshToken = data.refresh_token;
    this.tokenExpiresAt = Date.now() + data.expires_in * 1000;

    // Notify the plugin to save the tokens
    if (this.onTokenUpdate) {
      await this.onTokenUpdate(this.bearerToken, this.refreshToken, this.tokenExpiresAt);
    }

    return data;
  }

  private getAuthHeaders(): HeadersInit {
    if (this.bearerToken) {
      return {
        Authorization: `Bearer ${this.bearerToken}`,
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
      // Try refresh first, then fall back to login
      this.bearerToken = '';
      if (this.refreshToken && await this.refreshAccessToken()) {
        const retryHeaders = {
          ...options.headers,
          ...this.getAuthHeaders(),
        };
        return await fetch(url, { ...options, headers: retryHeaders });
      }

      // Refresh failed, try full login
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
    const response = await this.authenticatedFetch(`${this.serverHost}/api/v1/books?limit=1000`);
    if (!response.ok) {
      throw new Error(`Failed to fetch books: ${response.statusText}`);
    }
    return await response.json();
  }

  async getBookDetails(bookId: number): Promise<BookDetails> {
    const response = await this.authenticatedFetch(`${this.serverHost}/api/v1/books/${bookId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch book details: ${response.statusText}`);
    }
    return await response.json();
  }
}
