export type DifficultyLevel = "beginner" | "intermediate" | "advanced" | "expert";

export interface ExerciseRequest {
  difficulty: DifficultyLevel;
  key_signature: string;
  instrument: string;
  time_signature: string;
  tempo: number;
  bars: number;
}

export interface ExerciseResponse {
  abc_notation: string;
  difficulty: string;
  key_signature: string;
  instrument: string;
  time_signature: string;
  tempo: number;
  bars: number;
  token_usage?: number;
  estimated_cost_usd?: number;
}

export interface ErrorResponse {
  error: string;
  detail?: string;
}
