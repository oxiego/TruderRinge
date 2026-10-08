import os
import zipfile

# Dateien und Quellcodes des Angular-Frontends
files = {
    "truderringe-frontend/package.json": """{
  "name": "truderringe-frontend",
  "version": "0.1.0",
  "scripts": {
    "ng": "ng",
    "start": "ng serve",
    "build": "ng build"
  },
  "private": true,
  "dependencies": {
    "@angular/animations": "^17.0.0",
    "@angular/common": "^17.0.0",
    "@angular/compiler": "^17.0.0",
    "@angular/core": "^17.0.0",
    "@angular/forms": "^17.0.0",
    "@angular/platform-browser": "^17.0.0",
    "@angular/platform-browser-dynamic": "^17.0.0",
    "@angular/router": "^17.0.0",
    "rxjs": "~7.8.0",
    "tslib": "^2.3.0",
    "zone.js": "~0.14.0"
  },
  "devDependencies": {
    "@angular-devkit/build-angular": "^17.0.0",
    "@angular/cli": "^17.0.0",
    "@angular/compiler-cli": "^17.0.0",
    "typescript": "~5.2.0"
  }
}
""",
    "truderringe-frontend/angular.json": """{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "version": 1,
  "newProjectRoot": "projects",
  "projects": {
    "truderringe-frontend": {
      "projectType": "application",
      "schematics": {},
      "root": "",
      "sourceRoot": "src",
      "prefix": "app",
      "architect": {
        "build": {
          "builder": "@angular-devkit/build-angular:application",
          "options": {
            "outputPath": "dist/truderringe-frontend",
            "index": "src/index.html",
            "browser": "src/main.ts",
            "polyfills": ["zone.js"],
            "tsConfig": "tsconfig.app.json",
            "assets": ["src/favicon.ico", "src/assets"],
            "styles": ["src/styles.css"],
            "scripts": []
          }
        },
        "serve": {
          "builder": "@angular-devkit/build-angular:dev-server",
          "options": {
            "buildTarget": "truderringe-frontend:build"
          }
        }
      }
    }
  }
}
""",
    "truderringe-frontend/tsconfig.json": """{
  "compileOnSave": false,
  "compilerOptions": {
    "outDir": "./dist/out-tsc",
    "forceConsistentCasingInFileNames": true,
    "strict": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "sourceMap": true,
    "declaration": false,
    "experimentalDecorators": true,
    "moduleResolution": "node",
    "importHelpers": true,
    "target": "ES2022",
    "module": "ES2022",
    "useDefineForClassFields": false,
    "lib": ["ES2022", "dom"]
  },
  "angularCompilerOptions": {
    "enableI18nLegacyMessageIdFormat": false,
    "strictInjectionParameters": true,
    "strictInputAccessModifiers": true,
    "strictTemplates": true
  }
}
""",
    "truderringe-frontend/tsconfig.app.json": """{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "outDir": "./out-tsc/app",
    "types": []
  },
  "files": ["src/main.ts"],
  "include": ["src/**/*.d.ts"]
}
""",
    "truderringe-frontend/src/index.html": """<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>TruderRinge - Schießleiter Dashboard</title>
  <base href="/">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen">
  <app-root></app-root>
</body>
</html>
""",
    "truderringe-frontend/src/styles.css": """@tailwind base;
@tailwind components;
@tailwind utilities;
""",
    "truderringe-frontend/src/main.ts": """import { bootstrapApplication } from '@angular/platform-browser';
import { provideHttpClient } from '@angular/common/http';
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent, {
  providers: [
    provideHttpClient()
  ]
}).catch(err => console.error(err));
""",
    "truderringe-frontend/src/app/models/results.interface.ts": """export interface FleischpreisResult {
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
""",
    "truderringe-frontend/src/app/services/results.service.ts": """import { Injectable } from '@angular/core';
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
""",
    "truderringe-frontend/src/app/app.component.ts": """import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ResultsService } from './services/results.service';
import { FleischpreisResult, PokalResult } from './models/results.interface';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  fleischpreisList: FleischpreisResult[] = [];
  pokalList: PokalResult[] = [];
  loading = false;
  statusMessage = '';

  constructor(private resultsService: ResultsService) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.resultsService.getFleischpreisLeaderboard().subscribe({
      next: (data) => this.fleischpreisList = data,
      error: (err) => console.error('Fehler beim Laden der Fleischpreisdaten', err)
    });

    this.resultsService.getPokalLeaderboard().subscribe({
      next: (data) => this.pokalList = data,
      error: (err) => console.error('Fehler beim Laden der Pokaldaten', err)
    });
  }

  triggerImport(): void {
    this.loading = true;
    this.statusMessage = '';
    this.resultsService.triggerWmkImport().subscribe({
      next: (res) => {
        this.statusMessage = `✅ Import erfolgreich: ${res.imported_shots} Schüsse verarbeitet und zugeordnet.`;
        this.loading = false;
        this.loadData();
      },
      error: (err) => {
        this.statusMessage = '❌ Fehler beim Ausführen des WM-Shot Imports.';
        this.loading = false;
        console.error(err);
      }
    });
  }
}
""",
    "truderringe-frontend/src/app/app.component.html": """<header class="bg-slate-800 border-b border-slate-700 px-6 py-4 flex justify-between items-center shadow-lg">
  <div class="flex items-center space-x-3">
    <div class="bg-emerald-600 text-white p-2 rounded-lg font-bold text-xl">TR</div>
    <div>
      <h1 class="text-xl font-bold tracking-wide">TruderRinge (Angular FE)</h1>
      <p class="text-xs text-slate-400">SG Gemütlichkeit Trudering e.V.</p>
    </div>
  </div>
  <button (click)="triggerImport()" [disabled]="loading" class="bg-emerald-600 hover:bg-emerald-500 text-white font-medium px-4 py-2 rounded-lg shadow flex items-center space-x-2 transition disabled:opacity-50">
    <span *ngIf="!loading">📥 WM-Shot .wmk Import auslösen</span>
    <span *ngIf="loading" class="animate-pulse">Importiere Daten...</span>
  </button>
</header>

<main class="p-6 max-w-7xl mx-auto space-y-6">

  <div *ngIf="statusMessage" class="bg-emerald-900/50 border border-emerald-500 text-emerald-200 px-4 py-3 rounded-lg text-sm">
    {{ statusMessage }}
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

    <!-- Fleischpreis Leaderboard -->
    <div class="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold text-amber-400 flex items-center space-x-2">
          <span>[Fleischpreis]</span>
          <span>Fleischpreis Wertung (Best-Teiler)</span>
        </h2>
        <span class="text-xs bg-slate-700 px-2.5 py-1 rounded-full text-slate-300">Schuss 1–20</span>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-slate-700 text-xs text-slate-400 uppercase">
              <th class="pb-2">Rang</th>
              <th class="pb-2">Schütze</th>
              <th class="pb-2">Klasse</th>
              <th class="pb-2 text-right">Teiler</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-700/50 text-sm">
            <tr *ngFor="let row of fleischpreisList; let i = index" class="hover:bg-slate-700/30 transition">
              <td class="py-2.5 font-bold">{{ i + 1 }}</td>
              <td class="py-2.5 font-medium text-slate-200">{{ row.member_name }}</td>
              <td class="py-2.5">
                <span class="text-xs px-2 py-0.5 rounded bg-slate-700 text-slate-300">{{ row.class }}</span>
              </td>
              <td class="py-2.5 text-right font-mono font-bold text-amber-400">{{ row.teiler | number:'1.1-1' }}</td>
            </tr>
            <tr *ngIf="fleischpreisList.length === 0">
              <td colspan="4" class="py-4 text-center text-slate-500 text-xs">Noch keine Daten importiert. Klicke oben auf Import.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pokal / Jahrestabelle -->
    <div class="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold text-sky-400 flex items-center space-x-2">
          <span>[Pokal]</span>
          <span>Pokal / Jahrestabelle</span>
        </h2>
        <span class="text-xs bg-slate-700 px-2.5 py-1 rounded-full text-slate-300">Ringe & Zehntel</span>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-slate-700 text-xs text-slate-400 uppercase">
              <th class="pb-2">Schütze</th>
              <th class="pb-2">Klasse</th>
              <th class="pb-2 text-center">Schüsse</th>
              <th class="pb-2 text-right">Ringe (Zehntel)</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-700/50 text-sm">
            <tr *ngFor="let row of pokalList" class="hover:bg-slate-700/30 transition">
              <td class="py-2.5 font-medium text-slate-200">{{ row.name }}</td>
              <td class="py-2.5">
                <span class="text-xs px-2 py-0.5 rounded bg-slate-700 text-slate-300">{{ row.class }}</span>
              </td>
              <td class="py-2.5 text-center text-slate-400">{{ row.shot_count }}</td>
              <td class="py-2.5 text-right font-mono font-bold text-sky-400">
                <span>{{ row.total_rings }}</span>
                <span class="text-xs text-sky-300 font-normal"> ({{ row.total_tenths | number:'1.1-1' }})</span>
              </td>
            </tr>
            <tr *ngIf="pokalList.length === 0">
              <td colspan="4" class="py-4 text-center text-slate-500 text-xs">Noch keine Daten importiert. Klicke oben auf Import.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</main>
""",
    "truderringe-frontend/src/app/app.component.css": ""
}

# Ordnerstruktur anlegen & Dateien erzeugen
for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# ZIP-Archiv verpacken
with zipfile.ZipFile("truderringe-angular-fe.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
    for path in files.keys():
        zipf.write(path)

print("Angular Frontend ZIP erfolgreich erstellt: truderringe-angular-fe.zip")
