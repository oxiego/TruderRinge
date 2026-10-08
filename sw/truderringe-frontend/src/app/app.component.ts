import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ResultsService } from './services/results.service';
import { FleischpreisResult, PokalResult } from './models/results.interface';

interface MemberRecord {
  id: number;
  firstName: string;
  lastName: string;
  birthDate: string;
  className: string;
  discipline: string;
  disagId: number | null;
  wmShotId: string;
  active: boolean;
}

interface ClassSetup {
  name: string;
  mode: 'Fleischpreis' | 'Pokal';
  remainingPrizes: number;
  discipline: string;
  factor: number;
}

interface StandAssignment {
  stand: number;
  memberId: number;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  readonly navigation = [
    { id: 'dashboard', label: 'Übersicht', group: 'Arbeitsbereich' },
    { id: 'import', label: 'Datenimport', group: 'Arbeitsbereich' },
    { id: 'setup', label: 'Schießabend-Setup', group: 'Steuerung' },
    { id: 'rules', label: 'Rule Engine', group: 'Steuerung' },
    { id: 'members', label: 'Mitglieder', group: 'Verein' },
    { id: 'stands', label: 'Standbelegung', group: 'Verein' },
    { id: 'season', label: 'Saisontabellen', group: 'Auswertung' },
    { id: 'events', label: 'Schießspiele', group: 'Auswertung' }
  ];
  readonly navigationGroups = [
    { id: 'work', label: 'Arbeitsbereich', expanded: true, items: this.navigation.filter(item => item.group === 'Arbeitsbereich') },
    { id: 'control', label: 'Steuerung', expanded: true, items: this.navigation.filter(item => item.group === 'Steuerung') },
    { id: 'club', label: 'Verein', expanded: true, items: this.navigation.filter(item => item.group === 'Verein') },
    { id: 'reports', label: 'Auswertung', expanded: true, items: this.navigation.filter(item => item.group === 'Auswertung') }
  ];
  readonly classes = ['Pistole', 'Gewehr Herren', 'Damen', 'Jugend'];
  readonly disciplines = ['Luftpistole', 'Luftgewehr', 'Luftgewehr Auflage'];
  readonly stands = [1, 2, 3, 4, 5, 6, 7, 8];
  readonly eventTypes = [
    { id: 'koenig', label: 'Königsschießen' },
    { id: 'gaudi', label: 'Gaudischießen' },
    { id: 'er-und-sie', label: 'Er-und-Sie' },
    { id: 'ostern', label: 'Osterschießen' },
    { id: 'martini', label: 'Martinischießen' },
    { id: 'nikolaus', label: 'Nikolausschießen' }
  ];
  view = 'dashboard';
  today = new Date().toISOString().slice(0, 10);
  competitionDate = this.today;
  weekRule: 'odd-fleischpreis' | 'even-pokal' = 'odd-fleischpreis';
  selectedImportSource: 'wmk' | 'xml' | 'live' = 'wmk';
  selectedImportFile = '';
  initialActiveTarget = 'Fleischpreis · bester Teiler';
  initialPokalTarget = 'Pokal · Ringe und Zehntel';
  followupTarget = 'Pokal-Nachtrag';
  followupLimit = 10;
  specialTarget = 'Schießspiel / Sonderwertung';
  includePractice = 'Nein';
  selectedEvent = 'koenig';
  statusMessage = '';
  statusKind: 'success' | 'error' | 'info' = 'info';
  memberSearch = '';
  selectedMemberId: number | null = null;
  selectedStand: number | null = null;
  bestOf = 8;
  season = '2026/2027';
  eventName = 'Königsschießen';
  eventDate = this.today;
  eventShotLimit = 5;
  eventHidden = true;
  eventScoring = 'Bester Teiler';
  pairFirstId: number | null = null;
  pairSecondId: number | null = null;
  newMember: Omit<MemberRecord, 'id' | 'active'> = {
    firstName: '', lastName: '', birthDate: '', className: 'Gewehr Herren',
    discipline: 'Luftgewehr', disagId: null, wmShotId: ''
  };
  classSetups: ClassSetup[] = [
    { name: 'Pistole', mode: 'Fleischpreis', remainingPrizes: 3, discipline: 'Luftpistole', factor: 3.0 },
    { name: 'Gewehr Herren', mode: 'Fleischpreis', remainingPrizes: 5, discipline: 'Luftgewehr', factor: 1.0 },
    { name: 'Damen', mode: 'Pokal', remainingPrizes: 0, discipline: 'Luftgewehr', factor: 1.0 },
    { name: 'Jugend', mode: 'Fleischpreis', remainingPrizes: 2, discipline: 'Luftgewehr', factor: 1.0 }
  ];
  members: MemberRecord[] = [
    { id: 1, firstName: 'Max', lastName: 'Mustermann', birthDate: '', className: 'Pistole', discipline: 'Luftpistole', disagId: 101, wmShotId: '', active: true },
    { id: 2, firstName: 'Erika', lastName: 'Musterfrau', birthDate: '', className: 'Gewehr Herren', discipline: 'Luftgewehr', disagId: 102, wmShotId: '', active: true }
  ];
  assignments: StandAssignment[] = [{ stand: 1, memberId: 1 }, { stand: 2, memberId: 2 }];
  fleischpreisList: FleischpreisResult[] = [];
  pokalList: PokalResult[] = [];
  loading = false;

  constructor(private resultsService: ResultsService) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.resultsService.getFleischpreisLeaderboard().subscribe({
      next: (data) => this.fleischpreisList = data,
      error: (err) => {
        this.fleischpreisList = [];
        console.error('Fehler beim Laden der Fleischpreisdaten', err);
      }
    });

    this.resultsService.getPokalLeaderboard().subscribe({
      next: (data) => this.pokalList = data,
      error: (err) => {
        this.pokalList = [];
        console.error('Fehler beim Laden der Pokaldaten', err);
      }
    });
  }

  get currentNavigationLabel(): string {
    return this.navigation.find(item => item.id === this.view)?.label ?? 'Übersicht';
  }

  get filteredMembers(): MemberRecord[] {
    const query = this.memberSearch.trim().toLocaleLowerCase('de');
    return this.members.filter(member =>
      `${member.firstName} ${member.lastName} ${member.className}`.toLocaleLowerCase('de').includes(query)
    );
  }

  get activeFleischpreisClasses(): number {
    return this.classSetups.filter(item => item.mode === 'Fleischpreis' && item.remainingPrizes > 0).length;
  }

  get freeStands(): number[] {
    return this.stands.filter(stand => !this.assignments.some(assignment => assignment.stand === stand));
  }

  memberById(id: number): MemberRecord | undefined {
    return this.members.find(member => member.id === id);
  }

  isStandOccupied(stand: number): boolean {
    return this.assignments.some(assignment => assignment.stand === stand);
  }

  assignmentForStand(stand: number): StandAssignment | undefined {
    return this.assignments.find(assignment => assignment.stand === stand);
  }

  activeModeFor(className: string): string {
    const normalizedClass = className.toLocaleUpperCase('de').replaceAll('_', ' ');
    return this.classSetups.find(item => item.name.toLocaleUpperCase('de') === normalizedClass)?.mode ?? 'Pokal';
  }

  setView(id: string): void {
    this.view = id;
    this.statusMessage = '';
  }

  onImportFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.selectedImportFile = input.files?.[0]?.name ?? '';
  }

  saveSetup(): void {
    for (const setup of this.classSetups) {
      if (setup.remainingPrizes === 0 && setup.mode === 'Fleischpreis') {
        setup.mode = 'Pokal';
      }
    }
    this.showStatus('Klassen-Setup als lokaler Entwurf aktualisiert.', 'success');
  }

  saveRules(): void {
    this.showStatus('Regelsatz lokal übernommen. Die API unterstützt die Regelkonfiguration noch nicht.', 'info');
  }

  addMember(): void {
    if (!this.newMember.firstName.trim() || !this.newMember.lastName.trim()) {
      this.showStatus('Bitte Vor- und Nachname eintragen.', 'error');
      return;
    }
    this.members = [...this.members, { ...this.newMember, id: Math.max(0, ...this.members.map(item => item.id)) + 1, active: true }];
    this.newMember = { firstName: '', lastName: '', birthDate: '', className: 'Gewehr Herren', discipline: 'Luftgewehr', disagId: null, wmShotId: '' };
    this.showStatus('Mitglied im lokalen Arbeitsstand angelegt. Eine dauerhafte Speicherung benötigt den Mitglieder-Endpunkt.', 'info');
  }

  toggleMember(member: MemberRecord): void {
    member.active = !member.active;
    this.showStatus(`${member.firstName} ${member.lastName}: ${member.active ? 'aktiv' : 'inaktiv'} (lokaler Arbeitsstand).`, 'info');
  }

  assignStandToMember(): void {
    if (this.selectedMemberId === null || this.selectedStand === null) {
      this.showStatus('Bitte Schütze und Stand auswählen.', 'error');
      return;
    }
    this.assignments = [...this.assignments.filter(item => item.memberId !== this.selectedMemberId && item.stand !== this.selectedStand), { memberId: this.selectedMemberId, stand: this.selectedStand }];
    this.showStatus('Standbelegung lokal aktualisiert.', 'success');
  }

  releaseStand(stand: number): void {
    this.assignments = this.assignments.filter(item => item.stand !== stand);
    this.showStatus(`Stand ${stand} ist wieder frei.`, 'success');
  }

  saveEvent(): void {
    const eventLabel = this.eventTypes.find(item => item.id === this.selectedEvent)?.label ?? 'Wettbewerb';
    if (this.selectedEvent === 'er-und-sie' && (!this.pairFirstId || !this.pairSecondId || this.pairFirstId === this.pairSecondId)) {
      this.showStatus('Für Er-und-Sie bitte zwei unterschiedliche Schützen auswählen.', 'error');
      return;
    }
    this.showStatus(`${eventLabel} als lokaler Entwurf für ${this.eventDate} angelegt.`, 'success');
  }

  exportResults(): void {
    const rows = [['Name', 'Klasse', 'Ringe', 'Zehntel', 'Schüsse'], ...this.pokalList.map(row => [row.name, row.class, String(row.total_rings), String(row.total_tenths), String(row.shot_count)])];
    const csv = rows.map(row => row.map(value => `"${value.replaceAll('"', '""')}"`).join(';')).join('\n');
    const link = document.createElement('a');
    link.href = URL.createObjectURL(new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8' }));
    link.download = `truderringe-${this.season.replace('/', '-')}.csv`;
    link.click();
    URL.revokeObjectURL(link.href);
  }

  private showStatus(message: string, kind: 'success' | 'error' | 'info'): void {
    this.statusMessage = message;
    this.statusKind = kind;
  }

  triggerImport(): void {
    if (this.selectedImportSource !== 'wmk') {
      this.showStatus('XML- und Live-Import sind in der aktuellen Backend-Version noch nicht verfügbar.', 'info');
      return;
    }
    this.loading = true;
    this.statusMessage = '';
    this.resultsService.triggerWmkImport().subscribe({
      next: (res) => {
        this.showStatus(`Import erfolgreich: ${res.imported_shots} Schüsse verarbeitet und zugeordnet.`, 'success');
        this.loading = false;
        this.loadData();
      },
      error: (err) => {
        this.showStatus('WM-Shot-Import fehlgeschlagen. Der aktuelle Endpunkt verarbeitet die konfigurierte Serverdatei.', 'error');
        this.loading = false;
        console.error(err);
      }
    });
  }
}
