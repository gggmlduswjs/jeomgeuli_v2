// src/lib/http.ts - HTTP utilities and base API configuration
import { createError, ErrorCode, toAppError, type AppError } from '../types/errors';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';
const API_TIMEOUT = 30000; // 30초

/**
 * 타임아웃이 있는 fetch 래퍼
 */
async function fetchWithTimeout(
  url: string,
  options: RequestInit,
  timeout: number = API_TIMEOUT
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error: unknown) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw createError(ErrorCode.TIMEOUT_ERROR, 'Request timeout', error);
    }
    // 네트워크 에러
    throw createError(ErrorCode.NETWORK_ERROR, 'Network error', error);
  }
}

/**
 * HTTP 응답을 JSON으로 파싱 (에러 처리 포함)
 */
async function parseJsonResponse(response: Response): Promise<any> {
  try {
    const text = await response.text();
    if (!text) {
      return {};
    }
    return JSON.parse(text);
  } catch (error) {
    // JSON 파싱 실패 시 빈 객체 반환
    console.warn('[HTTP] JSON 파싱 실패:', error);
    return {};
  }
}

export const apiBase = API_BASE;

export const http = {
  /**
   * GET 요청
   */
  get: async (path: string, options?: RequestInit): Promise<any> => {
    try {
      const response = await fetchWithTimeout(
        `${API_BASE}${path}`,
        {
          method: 'GET',
          ...options,
          headers: {
            'Content-Type': 'application/json',
            ...options?.headers,
          },
        }
      );

      if (!response.ok) {
        const errorData = await parseJsonResponse(response);
        throw createError(
          ErrorCode.API_ERROR,
          errorData.detail || errorData.message || `HTTP ${response.status}`,
          { status: response.status, data: errorData },
          { status: response.status, data: errorData }
        );
      }

      return parseJsonResponse(response);
    } catch (error: unknown) {
      // 이미 AppError인 경우 그대로 throw
      if (error && typeof error === 'object' && 'code' in error) {
        throw error;
      }
      // 그 외의 경우 AppError로 변환
      throw toAppError(error);
    }
  },

  /**
   * POST 요청
   */
  post: async (path: string, body?: any, options?: RequestInit): Promise<any> => {
    try {
      const response = await fetchWithTimeout(
        `${API_BASE}${path}`,
        {
          method: 'POST',
          ...options,
          headers: {
            'Content-Type': 'application/json',
            ...options?.headers,
          },
          body: body ? JSON.stringify(body) : undefined,
        }
      );

      if (!response.ok) {
        const errorData = await parseJsonResponse(response);
        throw createError(
          ErrorCode.API_ERROR,
          errorData.detail || errorData.message || `HTTP ${response.status}`,
          { status: response.status, data: errorData },
          { status: response.status, data: errorData }
        );
      }

      return parseJsonResponse(response);
    } catch (error: unknown) {
      // 이미 AppError인 경우 그대로 throw
      if (error && typeof error === 'object' && 'code' in error) {
        throw error;
      }
      // 그 외의 경우 AppError로 변환
      throw toAppError(error);
    }
  },

  /**
   * FormData POST 요청 (파일 업로드용)
   */
  postFormData: async (path: string, formData: FormData, options?: RequestInit): Promise<any> => {
    try {
      const response = await fetchWithTimeout(
        `${API_BASE}${path}`,
        {
          method: 'POST',
          ...options,
          // Content-Type 헤더를 설정하지 않음 (브라우저가 자동으로 multipart/form-data 설정)
          body: formData,
        }
      );

      if (!response.ok) {
        const errorData = await parseJsonResponse(response);
        throw createError(
          ErrorCode.API_ERROR,
          errorData.error || errorData.detail || errorData.message || `HTTP ${response.status}`,
          { status: response.status, data: errorData },
          { status: response.status, data: errorData }
        );
      }

      return parseJsonResponse(response);
    } catch (error: unknown) {
      // 이미 AppError인 경우 그대로 throw
      if (error && typeof error === 'object' && 'code' in error) {
        throw error;
      }
      // 그 외의 경우 AppError로 변환
      throw toAppError(error);
    }
  },
};

export const api = http;
