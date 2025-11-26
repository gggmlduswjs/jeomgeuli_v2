// src/lib/api.ts - Legacy API functions (DEPRECATED)
// This file is kept for backward compatibility but should not be used in new code.
// Use Facade APIs from lib/api/*.ts instead.

import { http, apiBase } from './http';
import { isAppError, toAppError } from '../types/errors';
import performanceMonitor from './performance';

export const API_BASE = apiBase;

// Types are now in types/api.ts - re-exported for backward compatibility
import type {
  ChatResponse,
  ExploreResponse,
  BrailleConvertResponse,
  LearnResponse,
  Textbook,
  Unit,
  Question,
  AnswerResult,
  PassageStructure,
  GraphPatterns,
  TextbookConvertResponse,
  CompressTextResponse,
  SentenceSummaryResponse,
} from '../types/api';

export type {
  ChatResponse,
  ExploreResponse,
  BrailleConvertResponse,
  LearnResponse,
  Textbook,
  Unit,
  Question,
  AnswerResult,
  PassageStructure,
  GraphPatterns,
  TextbookConvertResponse,
  CompressTextResponse,
  SentenceSummaryResponse,
};

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

// Types moved to types/api.ts - see re-export at top of file

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

// Types moved to types/api.ts - see re-export at top of file

// New Jeomgeuli-Suneung API Functions
export async function listTextbooks(): Promise<Textbook[]> {
  const startTime = Date.now();
  try {
    const response = await http.get('/exam/textbook/');
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('listTextbooks', duration, true);
    return response.textbooks || [];
  } catch (error: unknown) {
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('listTextbooks', duration, false);
    console.error('[API] listTextbooks error:', error);
    return [];
  }
}

export async function listUnits(textbookId: number): Promise<Unit[]> {
  const startTime = Date.now();
  try {
    const response = await http.get(`/exam/textbook/${textbookId}/units/`);
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('listUnits', duration, true);
    return response.units || [];
  } catch (error: unknown) {
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('listUnits', duration, false);
    console.error('[API] listUnits error:', error);
    return [];
  }
}

export async function getUnit(unitId: number): Promise<Unit | null> {
  const startTime = Date.now();
  try {
    const response = await http.get(`/exam/unit/${unitId}/`);
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('getUnit', duration, true);
    return response.unit || null;
  } catch (error: unknown) {
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('getUnit', duration, false);
    console.error('[API] getUnit error:', error);
    return null;
  }
}

export async function getQuestion(questionId: number): Promise<Question | null> {
  const startTime = Date.now();
  try {
    const response = await http.get(`/exam/question/${questionId}/`);
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('getQuestion', duration, true);
    return response.question || null;
  } catch (error: unknown) {
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('getQuestion', duration, false);
    console.error('[API] getQuestion error:', error);
    return null;
  }
}

export async function submitAnswer(questionId: number, answer: number, responseTime?: number): Promise<AnswerResult | null> {
  const startTime = Date.now();
  try {
    const response = await http.post('/exam/submit/', {
      question_id: questionId,
      answer,
      response_time: responseTime,
    });
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('submitAnswer', duration, true);
    return {
      is_correct: response.is_correct,
      correct_answer: response.correct_answer,
      explanation: response.explanation,
    };
  } catch (error: unknown) {
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('submitAnswer', duration, false);
    console.error('[API] submitAnswer error:', error);
    return null;
  }
}

export async function startExam(): Promise<{ exam_id: number; started_at: string } | null> {
  const startTime = Date.now();
  try {
    const response = await http.post('/exam/start/');
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('startExam', duration, true);
    return {
      exam_id: response.exam_id,
      started_at: response.started_at,
    };
  } catch (error: unknown) {
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('startExam', duration, false);
    console.error('[API] startExam error:', error);
    return null;
  }
}

export async function analyzePassage(passage: string): Promise<PassageStructure | null> {
  const startTime = Date.now();
  try {
    const response = await http.post('/learn/passage-analyze/', { passage });
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('analyzePassage', duration, true);
    return response.structure || null;
  } catch (error: unknown) {
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('analyzePassage', duration, false);
    console.error('[API] analyzePassage error:', error);
    return null;
  }
}

export async function analyzeGraph(imageFile: File): Promise<GraphPatterns | null> {
  const startTime = Date.now();
  try {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    const response = await http.postFormData('/exam/graph-analyze/', formData);
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('analyzeGraph', duration, true);
    return response.patterns || null;
  } catch (error: unknown) {
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('analyzeGraph', duration, false);
    console.error('[API] analyzeGraph error:', error);
    return null;
  }
}

export async function getTodayVocab(): Promise<{ vocab: any[]; sisa: any[] } | null> {
  const startTime = Date.now();
  try {
    const response = await http.get('/vocab/today/');
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('getTodayVocab', duration, true);
    return {
      vocab: response.vocab || [],
      sisa: response.sisa || [],
    };
  } catch (error: unknown) {
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('getTodayVocab', duration, false);
    console.error('[API] getTodayVocab error:', error);
    return null;
  }
}

export async function getNews(): Promise<{ news: any[]; sisa: any[] } | null> {
  const startTime = Date.now();
  try {
    const response = await http.get('/explore/news/');
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('getNews', duration, true);
    return {
      news: response.news || [],
      sisa: response.sisa || [],
    };
  } catch (error: unknown) {
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('getNews', duration, false);
    console.error('[API] getNews error:', error);
    return null;
  }
}

export async function generateBraillePattern(
  type: 'answer' | 'trend' | 'number' | 'status',
  data: any
): Promise<number[] | null> {
  const startTime = Date.now();
  try {
    const response = await http.post('/braille/pattern/', { type, data });
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('generateBraillePattern', duration, true);
    return response.pattern || null;
  } catch (error: unknown) {
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('generateBraillePattern', duration, false);
    console.error('[API] generateBraillePattern error:', error);
    return null;
  }
}

export async function logAnalytics(type: string, data: any): Promise<boolean> {
  const startTime = Date.now();
  try {
    const response = await http.post('/analytics/log/', { type, ...data });
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('logAnalytics', duration, true);
    return response.ok === true;
  } catch (error: unknown) {
    const duration = Date.now() - startTime;
    performanceMonitor.measureAPICall('logAnalytics', duration, false);
    console.error('[API] logAnalytics error:', error);
    return false;
  }
}

