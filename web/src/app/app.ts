import { DecimalPipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, computed, inject, signal } from '@angular/core';

import { API_URL, MIN_TEXT_LENGTH } from './config';
import { EXAMPLES, Example } from './examples';
import { PredictResponse } from './models';
import { ScoreList } from './score-list';
import { TriageService } from './triage.service';
import { Trends } from './trends';

@Component({
  imports: [DecimalPipe, ScoreList, Trends],
  selector: 'app-root',
  styleUrl: './app.css',
  templateUrl: './app.html',
})
export class App {
  private readonly triage = inject(TriageService);

  protected readonly examples = EXAMPLES;
  protected readonly minLength = MIN_TEXT_LENGTH;
  protected readonly view = signal<'classify' | 'trends'>('classify');
  protected readonly text = signal('');
  protected readonly loading = signal(false);
  protected readonly error = signal<string | null>(null);
  protected readonly result = signal<PredictResponse | null>(null);
  protected readonly canSubmit = computed(
    () => this.text().trim().length >= MIN_TEXT_LENGTH && !this.loading(),
  );

  protected onInput(event: Event): void {
    this.text.set((event.target as HTMLTextAreaElement).value);
  }

  protected useExample(example: Example): void {
    this.text.set(example.text);
    this.result.set(null);
    this.error.set(null);
  }

  protected submit(): void {
    this.loading.set(true);
    this.error.set(null);
    this.triage.predict(this.text().trim()).subscribe({
      next: (response) => {
        this.result.set(response);
        this.loading.set(false);
      },
      error: (failure: HttpErrorResponse) => {
        this.result.set(null);
        this.error.set(this.describe(failure));
        this.loading.set(false);
      },
    });
  }

  private describe(failure: HttpErrorResponse): string {
    if (failure.status === 0) {
      return `Cannot reach the API at ${API_URL}. Is it running?`;
    }
    if (failure.status === 422) {
      return `The report must be at least ${MIN_TEXT_LENGTH} characters long.`;
    }
    return `The API returned an error (${failure.status}).`;
  }
}
