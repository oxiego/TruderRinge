import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { FleischpreisResult, PokalResult, ImportResponse } from '../models/results.interface';

@Injectable({
  providedIn: 'root'
})
export class ResultsService {
  private baseUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  getFleischpreisLeaderboard(): Observable<FleischpreisResult[]> {
    return this.http.get<FleischpreisResult[]>(`${this.baseUrl}/results/fleischpreis`);
  }

  getPokalLeaderboard(): Observable<PokalResult[]> {
    return this.http.get<PokalResult[]>(`${this.baseUrl}/results/pokal`);
  }

  triggerWmkImport(): Observable<ImportResponse> {
    return this.http.post<ImportResponse>(`${this.baseUrl}/import/wmk`, {});
  }
}
