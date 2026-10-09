import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { ResultsService } from './services/results.service';
import {
  FleischpreisResult,
  ImportPreview,
  ImportResponse,
  MemberRecord,
  PokalResult
} from './models/results.interface';

type Section = 'overview' | 'members' | 'season' | 'shooting-days' | 'results' | 'reports' | 'import';
type NoticeKind = 'success' | 'error' | 'info';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  readonly navigation: { id: Section; label: string; icon: string }[] = [
    { id: 'overview', label: 'Übersicht', icon: '⌂' },
    { id: 'members', label: 'Mitglieder', icon: '◎' },
    { id: 'season', label: 'Saison & Klassen', icon: '◷' },
    { id: 'shooting-days', label: 'Schießtage', icon: '◉' },
    { id: 'results', label: 'Ergebnisse & Wertungen', icon: '↗' },
    { id: 'reports', label: 'Berichte', icon: '▤' },
    { id: 'import', label: 'Datenimport', icon: '↓' }
  ];
  readonly today = new Date();

  section: Section = 'overview';
  apiAvailable = false;
  busy = false;
  showMemberForm = false;
  editingMemberId: number | null = null;
  showImportPreview = false;
  notice = '';
  noticeKind: NoticeKind = 'info';
  memberSearch = '';
  members: MemberRecord[] = [];
  meatResults: FleischpreisResult[] = [];
  cupResults: PokalResult[] = [];
  selectedFile: File | null = null;
  competitionDate = this.localDateString(new Date());
  importPreview: ImportPreview | null = null;
  importResponse: ImportResponse | null = null;

  newMember = this.emptyMember();

  constructor(private readonly resultsService: ResultsService) {}

  ngOnInit(): void {
    this.refresh();
  }

  get sectionLabel(): string {
    return this.navigation.find((item) => item.id === this.section)?.label ?? 'Übersicht';
  }

  get filteredMembers(): MemberRecord[] {
    const query = this.memberSearch.trim().toLocaleLowerCase('de');
    if (!query) return this.members;
    return this.members.filter((member) =>
      `${member.first_name} ${member.last_name} ${member.member_number ?? ''} ${member.disag_start_number ?? ''}`
        .toLocaleLowerCase('de')
        .includes(query)
    );
  }

  get activeMembers(): number {
    return this.members.filter((member) => member.active).length;
  }

  setSection(section: Section): void {
    this.section = section;
    this.notice = '';
  }

  refresh(): void {
    this.resultsService.getHealth().subscribe({
      next: () => this.apiAvailable = true,
      error: () => this.apiAvailable = false
    });
    this.loadMembers();
    this.loadResults();
  }

  loadMembers(): void {
    this.resultsService.getMembers().subscribe({
      next: (members) => this.members = members,
      error: (error: HttpErrorResponse) => this.setNotice(this.errorMessage(error, 'Mitglieder konnten nicht geladen werden.'), 'error')
    });
  }

  loadResults(): void {
    this.resultsService.getFleischpreisLeaderboard().subscribe({
      next: (results) => this.meatResults = results,
      error: (error: HttpErrorResponse) => {
        this.meatResults = [];
        this.setNotice(this.errorMessage(error, 'Fleischpreis-PoC-Daten konnten nicht geladen werden.'), 'error');
      }
    });
    this.resultsService.getPokalLeaderboard().subscribe({
      next: (results) => this.cupResults = results,
      error: (error: HttpErrorResponse) => {
        this.cupResults = [];
        this.setNotice(this.errorMessage(error, 'Pokal-PoC-Daten konnten nicht geladen werden.'), 'error');
      }
    });
  }

  addMember(): void {
    this.busy = true;
    const payload = {
      ...this.newMember,
      member_number: (this.newMember.member_number ?? '').trim() || null,
      disag_start_number: this.newMember.disag_start_number || null
    };
    if (this.editingMemberId !== null) {
      this.resultsService.updateMember(this.editingMemberId, payload).subscribe({
        next: (member) => {
          this.members = this.members.map((item) => item.id === member.id ? member : item);
          this.resetMemberForm();
          this.busy = false;
          this.setNotice('Mitgliedsdaten wurden gespeichert.', 'success');
        },
        error: (error: HttpErrorResponse) => {
          this.busy = false;
          this.setNotice(this.errorMessage(error, 'Mitgliedsdaten konnten nicht gespeichert werden.'), 'error');
        }
      });
      return;
    }
    this.resultsService.createMember(payload).subscribe({
      next: (member) => {
        this.members = [...this.members, member].sort((a, b) =>
          `${a.last_name} ${a.first_name}`.localeCompare(`${b.last_name} ${b.first_name}`, 'de')
        );
        this.resetMemberForm();
        this.busy = false;
        this.setNotice('Mitglied wurde dauerhaft gespeichert.', 'success');
      },
      error: (error: HttpErrorResponse) => {
        this.busy = false;
        this.setNotice(this.errorMessage(error, 'Mitglied konnte nicht gespeichert werden.'), 'error');
      }
    });
  }

  editMember(member: MemberRecord): void {
    this.editingMemberId = member.id;
    this.newMember = {
      first_name: member.first_name,
      last_name: member.last_name,
      member_number: member.member_number ?? '',
      birth_date: member.birth_date,
      gender: member.gender,
      disag_start_number: member.disag_start_number,
      lg_participation: member.lg_participation,
      lp_participation: member.lp_participation,
      lg_fleisch_eligible: member.lg_fleisch_eligible,
      lp_fleisch_eligible: member.lp_fleisch_eligible,
      uses_aids: member.uses_aids,
      active: member.active,
      last_year_average_lg: member.last_year_average_lg,
      last_year_average_lp: member.last_year_average_lp
    };
    this.showMemberForm = true;
  }

  toggleMember(member: MemberRecord): void {
    this.resultsService.updateMember(member.id, { active: !member.active }).subscribe({
      next: (updated) => {
        this.members = this.members.map((item) => item.id === updated.id ? updated : item);
        this.setNotice(`${updated.first_name} ${updated.last_name} ist jetzt ${updated.active ? 'aktiv' : 'inaktiv'}.`, 'success');
      },
      error: (error: HttpErrorResponse) => this.setNotice(this.errorMessage(error, 'Mitgliedsstatus konnte nicht geändert werden.'), 'error')
    });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.selectedFile = input.files?.[0] ?? null;
    this.importPreview = null;
    this.importResponse = null;
  }

  previewImport(): void {
    if (!this.selectedFile) {
      this.setNotice('Bitte zuerst eine WMK-Datei auswählen.', 'error');
      return;
    }
    this.busy = true;
    this.resultsService.previewWmkImport(this.selectedFile).subscribe({
      next: (preview) => {
        this.importPreview = preview;
        this.importResponse = null;
        this.showImportPreview = true;
        this.busy = false;
        this.setNotice('Vorschau erstellt. Unbekannte DISAG-Startnummern müssen vor dem Import geklärt werden.', 'info');
      },
      error: (error: HttpErrorResponse) => {
        this.busy = false;
        this.setNotice(this.errorMessage(error, 'WMK-Datei konnte nicht geprüft werden.'), 'error');
      }
    });
  }

  importResults(): void {
    if (!this.selectedFile || !this.importPreview) return;
    if (!this.competitionDate) {
      this.setNotice('Bitte ein Schießdatum auswählen.', 'error');
      return;
    }
    if (this.importPreview.unknown_start_numbers.length) {
      this.setNotice('Import gestoppt: Bitte ordne die unbekannten Startnummern zuerst bestehenden Mitgliedern zu.', 'error');
      return;
    }
    this.busy = true;
    this.resultsService.importWmk(this.selectedFile, this.competitionDate).subscribe({
      next: (response) => {
        this.importResponse = response;
        this.busy = false;
        const rejected = response.rejected_shots.length;
        this.setNotice(
          rejected
            ? `${response.imported_shots} Schüsse importiert; ${rejected} Schüsse wurden mit Fehlerhinweisen zurückgewiesen.`
            : `${response.imported_shots} Schüsse importiert.`,
          rejected ? 'info' : 'success'
        );
        this.loadResults();
      },
      error: (error: HttpErrorResponse) => {
        this.busy = false;
        this.setNotice(this.errorMessage(error, 'WMK-Import fehlgeschlagen.'), 'error');
      }
    });
  }

  clearNotice(): void {
    this.notice = '';
  }

  resetMemberForm(): void {
    this.newMember = this.emptyMember();
    this.editingMemberId = null;
    this.showMemberForm = false;
  }

  private emptyMember(): Omit<MemberRecord, 'id' | 'category_class'> {
    return {
      first_name: '',
      last_name: '',
      member_number: '',
      birth_date: '',
      gender: 'M',
      disag_start_number: null,
      lg_participation: true,
      lp_participation: false,
      lg_fleisch_eligible: false,
      lp_fleisch_eligible: false,
      uses_aids: false,
      active: true,
      last_year_average_lg: null,
      last_year_average_lp: null
    };
  }

  private localDateString(value: Date): string {
    const month = String(value.getMonth() + 1).padStart(2, '0');
    const day = String(value.getDate()).padStart(2, '0');
    return `${value.getFullYear()}-${month}-${day}`;
  }

  private setNotice(message: string, kind: NoticeKind): void {
    this.notice = message;
    this.noticeKind = kind;
  }

  private errorMessage(error: HttpErrorResponse, fallback: string): string {
    const detail = error.error?.detail;
    return typeof detail === 'string' ? detail : fallback;
  }
}
