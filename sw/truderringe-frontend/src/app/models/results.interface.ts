export interface FleischpreisResult {
  member_name: string;
  class: string;
  teiler: number;
  shot_number: number;
}

export interface PokalResult {
  name: string;
  class: string;
  total_rings: number;
  total_tenths: number;
  shot_count: number;
}

export interface ImportResponse {
  status: string;
  imported_shots: number;
}
