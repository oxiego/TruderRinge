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
  rejected_shots: {
    disag_start_number: number;
    shot_number: number;
    reason: string;
  }[];
}

export interface ImportPreview {
  shot_count: number;
  shooter_count: number;
  unknown_start_numbers: number[];
}

export interface MemberRecord {
  id: number;
  first_name: string;
  last_name: string;
  member_number: string | null;
  birth_date: string | null;
  gender: 'M' | 'W' | null;
  disag_start_number: number | null;
  category_class: string | null;
  lg_participation: boolean;
  lp_participation: boolean;
  lg_fleisch_eligible: boolean;
  lp_fleisch_eligible: boolean;
  uses_aids: boolean;
  active: boolean;
  last_year_average_lg: number | null;
  last_year_average_lp: number | null;
}
