export interface WordItem {
  word: string;
  frequency: number;
  is_removed?: boolean;
}

export interface Session {
  id: string;
  language: 'en' | 'jp';
  filename: string;
  status: 'uploaded' | 'processed' | 'finalized';
  styles?: string[];
}

export interface ProcessResponse {
  words: WordItem[];
}

export interface WordListResponse {
  words: WordItem[];
  total: number;
}

export interface FinalizeResponse {
  top_words: string[];
  learned_count: number;
  total_count: number;
}

export interface KnownWordsResponse {
  words: string[];
  count: number;
}
