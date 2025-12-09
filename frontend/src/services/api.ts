import axios from 'axios';
import type { Session, ProcessResponse, WordListResponse, FinalizeResponse, KnownWordsResponse } from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadSubtitle = async (file: File): Promise<Session> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<Session>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const processSession = async (sessionId: string, style?: string): Promise<ProcessResponse> => {
  const response = await api.post<ProcessResponse>(`/session/${sessionId}/process`, { style });
  return response.data;
};

export const getSessionWords = async (sessionId: string): Promise<WordListResponse> => {
  const response = await api.get<WordListResponse>(`/session/${sessionId}/words`);
  return response.data;
};

export const updateSessionWords = async (sessionId: string, removedWords: string[]): Promise<void> => {
  await api.patch(`/session/${sessionId}/words`, { removed_words: removedWords });
};

export const finalizeSession = async (sessionId: string): Promise<FinalizeResponse> => {
  const response = await api.post<FinalizeResponse>(`/session/${sessionId}/finalize`);
  return response.data;
};

export const getKnownWords = async (language: string): Promise<KnownWordsResponse> => {
  const response = await api.get<KnownWordsResponse>(`/known-words/${language}`);
  return response.data;
};

export default api;
