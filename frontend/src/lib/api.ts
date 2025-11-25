// src/lib/api.ts - API functions

import { http, apiBase } from './http';
import { isAppError, toAppError, ErrorCode, type AppError } from '../types/errors';
import performanceMonitor from './performance';

export const API_BASE = apiBase;

// Types
export interface ChatResponse {
  answer: string;
  keywords?: string[];
  ok?: boolean;
  error?: string;
}

export interface ExploreResponse {
  answer: string;
  news: any[];
  query: string;
  ok?: boolean;
  error?: string;
}

export interface BrailleConvertResponse {
  cells: number[][];
  ok?: boolean;
  error?: string;
}

export interface LearnResponse {
  mode?: string;
  title?: string;
  items: any[];
  ok?: boolean;
}

// Chat API
export async function askChat(query: string): Promise<ChatResponse> {
  const startTime = Date.now();
  try {
    const response = await http.post('/chat/ask/', { query });
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('askChat', duration, true);
    
    return {
      answer: response.answer || '',
      keywords: response.keywords || [],
      ok: response.ok !== false,
    };
  } catch (error: unknown) {
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('askChat', duration, false);
    console.error('[API] askChat error:', error);
    const appError = isAppError(error) ? error : toAppError(error);
    
    return {
      answer: `질문 처리 중 오류가 발생했습니다: ${appError.userMessage}`,
      keywords: [],
      ok: false,
      error: appError.message,
    };
  }
}

export async function askChatWithKeywords(query: string): Promise<ChatResponse> {
  return askChat(query);
}

// Explore API
export async function fetchExplore(query: string): Promise<ExploreResponse> {
  const startTime = Date.now();
  try {
    const response = await http.post('/explore/', { query });
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('fetchExplore', duration, true);
    
    return {
      answer: response.answer || '',
      news: response.news || [],
      query: response.query || query,
      ok: response.ok !== false,
    };
  } catch (error: unknown) {
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('fetchExplore', duration, false);
    console.error('[API] fetchExplore error:', error);
    
    // AppError로 변환되어 있음
    const appError = isAppError(error) ? error : toAppError(error);
    
    // Fallback 응답 반환
    return {
      answer: `정보를 가져오는 중 오류가 발생했습니다: ${appError.userMessage}`,
      news: [],
      query,
      ok: false,
      error: appError.message,
    };
  }
}

// Braille API
export async function convertBraille(
  text: string,
  _mode?: string
): Promise<BrailleConvertResponse> {
  try {
    // POST 요청으로 /api/braille/convert/ 호출
    const response = await http.post('/braille/convert/', { text });
    return {
      cells: response.cells || [],
      ok: response.ok !== false,
    };
  } catch (error: unknown) {
    const appError = isAppError(error) ? error : toAppError(error);
    
    // 404 에러인 경우 /api/convert/로 fallback (레거시 호환)
    if (appError.status === 404 || appError.message.includes('404')) {
      try {
        const fallbackResponse = await http.post('/convert/', { text });
        return {
          cells: fallbackResponse.cells || [],
          ok: fallbackResponse.ok !== false,
        };
      } catch (fallbackError: unknown) {
        const fallbackAppError = isAppError(fallbackError) ? fallbackError : toAppError(fallbackError);
        console.error('[API] convertBraille fallback error:', fallbackAppError);
        return {
          cells: [],
          ok: false,
          error: fallbackAppError.message,
        };
      }
    }
    
    console.error('[API] convertBraille error:', appError);
    return {
      cells: [],
      ok: false,
      error: appError.message,
    };
  }
}

// Learn API
export async function fetchLearn(mode: string): Promise<LearnResponse> {
  try {
    const modeMap: Record<string, string> = {
      char: 'chars',
      word: 'words',
      sentence: 'sentences',
      keyword: 'keywords',
    };
    
    const endpoint = modeMap[mode] || mode;
    const response = await http.get(`/learn/${endpoint}/`);
    
    // Handle different response formats
    if (response.items) {
      return {
        mode: response.mode || mode,
        items: response.items,
        ok: response.ok !== false,
      };
    }
    
    // If response is directly an array or has mode/items structure
    return {
      mode: response.mode || mode,
      items: Array.isArray(response) ? response : response.items || [],
      ok: response.ok !== false,
    };
  } catch (error: unknown) {
    console.error('[API] fetchLearn error:', error);
    const appError = isAppError(error) ? error : toAppError(error);
    
    return {
      mode,
      items: [],
      ok: false,
    };
  }
}

// Review/Learning API
export async function saveReview(
  kind: 'wrong' | 'keyword',
  payload: any
): Promise<{ ok: boolean }> {
  try {
    const response = await http.post('/learning/save/', { kind, payload });
    return { ok: response.ok !== false };
  } catch (error: unknown) {
    console.error('[API] saveReview error:', error);
    const appError = isAppError(error) ? error : toAppError(error);
    return { ok: false };
  }
}

// Health API
export async function health(): Promise<{ ok: boolean }> {
  try {
    const response = await http.get('/health/');
    return { ok: response.ok !== false };
  } catch {
    return { ok: false };
  }
}

// Utility function to normalize answer text
export function normalizeAnswer(response: ChatResponse | null | undefined): string {
  if (!response) return '';
  return response.answer || '';
}

// Exam API Types
export interface TextbookConvertResponse {
  braille_cells: number[][];
  braille_text: string;
  original_text: string;
  text_length: number;
  cells_count: number;
  pages_count: number;
  error?: string;
}

export interface CompressTextResponse {
  compressed_text: string;
  original_length: number;
  compressed_length: number;
  compression_ratio: number;
  mode: string;
  error?: string;
}

export interface SentenceSummaryResponse {
  summary: string;
  original: string;
  error?: string;
}

// Exam API Functions
export async function convertTextbook(pdfFile: File): Promise<TextbookConvertResponse> {
  const startTime = Date.now();
  try {
    const formData = new FormData();
    formData.append('pdf', pdfFile);
    
    const response = await http.postFormData('/exam/convert-textbook/', formData);
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('convertTextbook', duration, true);
    
    return {
      braille_cells: response.braille_cells || [],
      braille_text: response.braille_text || '',
      original_text: response.original_text || '',
      text_length: response.text_length || 0,
      cells_count: response.cells_count || 0,
      pages_count: response.pages_count || 0,
    };
  } catch (error: unknown) {
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('convertTextbook', duration, false);
    console.error('[API] convertTextbook error:', error);
    const appError = isAppError(error) ? error : toAppError(error);
    throw appError;
  }
}

export async function compressText(
  text: string,
  mode: 'compressed' | 'outline' = 'compressed',
  targetRatio: number = 0.3
): Promise<CompressTextResponse> {
  const startTime = Date.now();
  try {
    const response = await http.post('/exam/compress/', {
      text,
      mode,
      targetRatio,
    });
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('compressText', duration, true);
    return {
      compressed_text: response.compressed_text || '',
      original_length: response.original_length || 0,
      compressed_length: response.compressed_length || 0,
      compression_ratio: response.compression_ratio || 0,
      mode: response.mode || mode,
    };
  } catch (error: unknown) {
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('compressText', duration, false);
    console.error('[API] compressText error:', error);
    const appError = isAppError(error) ? error : toAppError(error);
    throw appError;
  }
}

export async function getSentenceSummary(sentence: string): Promise<string> {
  const startTime = Date.now();
  try {
    const response = await http.post('/exam/sentence-summary/', { sentence });
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('getSentenceSummary', duration, true);
    return response.summary || '';
  } catch (error: unknown) {
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('getSentenceSummary', duration, false);
    console.error('[API] getSentenceSummary error:', error);
    return ''; // 실패 시 빈 문자열 반환 (선택적 기능이므로)
  }
}

