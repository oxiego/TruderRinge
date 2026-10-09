import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  FleischpreisResult,
  ImportPreview,
  ImportResponse,
  MemberRecord,
  PokalResult
} from '../models/results.interface';

@Injectable({
  providedIn: 'root'
})
export class ResultsService {
  private readonly baseUrl = 'http://127.0.0.1:8000';

  constructor(private readonly http: HttpClient) {}

  getHealth(): Observable<{ status: string }> {
    return this.http.get<{ status: string }>(`${this.baseUrl}/health`);
  }

  getMembers(): Observable<MemberRecord[]> {
    return this.http.get<MemberRecord[]>(`${this.baseUrl}/members`);
  }

  createMember(member: Omit<MemberRecord, 'id' | 'category_class'>): Observable<MemberRecord> {
    return this.http.post<MemberRecord>(`${this.baseUrl}/members`, member);
  }

  updateMember(id: number, changes: Partial<MemberRecord>): Observable<MemberRecord> {
    return this.http.patch<MemberRecord>(`${this.baseUrl}/members/${id}`, changes);
  }

  getFleischpreisLeaderboard(): Observable<FleischpreisResult[]> {
    return this.http.get<FleischpreisResult[]>(`${this.baseUrl}/results/fleischpreis`);
  }

  getPokalLeaderboard(): Observable<PokalResult[]> {
    return this.http.get<PokalResult[]>(`${this.baseUrl}/results/pokal`);
  }

  previewWmkImport(file: File): Observable<ImportPreview> {
    return this.http.post<ImportPreview>(`${this.baseUrl}/import/wmk/preview`, file, {
      headers: { 'Content-Type': 'application/octet-stream' }
    });
  }

  importWmk(file: File, competitionDate: string): Observable<ImportResponse> {
    return this.http.post<ImportResponse>(
      `${this.baseUrl}/import/wmk?competition_date=${encodeURIComponent(competitionDate)}`,
      file,
      { headers: { 'Content-Type': 'application/octet-stream' } }
    );
  }
}
