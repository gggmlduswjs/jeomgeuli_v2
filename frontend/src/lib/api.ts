/**
 * @deprecated 이 파일은 레거시 호환성을 위해 유지됩니다.
 * 새로운 코드에서는 lib/api/*.ts 모듈을 직접 사용하세요.
 * 
 * 예시:
 * - import { examAPI } from './lib/api/exam';
 * - import { chatAPI } from './lib/api/chat';
 * - 또는 import { examAPI, chatAPI } from './lib/api';
 */

// 모든 API를 새 모듈에서 re-export
export * from './api';

// API_BASE는 http에서 re-export
export { apiBase as API_BASE } from './http';
