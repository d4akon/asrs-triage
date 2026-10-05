import { DecimalPipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';

import { LineChart, Series } from './line-chart';
import { LabelTrend, LabelTrends, TopicTrends } from './models';
import { TriageService } from './triage.service';

const WELL_TRACKED = 0.6;
const COVID_BAND = { from: '2020-03', to: '2020-05' };

@Component({
  selector: 'app-trends',
  imports: [DecimalPipe, LineChart],
  templateUrl: './trends.html',
  styleUrl: './trends.css',
})
export class Trends {
  private readonly triage = inject(TriageService);

  protected readonly covid = COVID_BAND;
  protected readonly labelData = signal<LabelTrends | null>(null);
  protected readonly topicData = signal<TopicTrends | null>(null);
  protected readonly error = signal<string | null>(null);
  protected readonly mode = signal<'labels' | 'topics'>('labels');
  protected readonly selectedLabel = signal<string>('');
  protected readonly selectedTopic = signal<number>(0);

  protected readonly labels = computed(() =>
    [...(this.labelData()?.labels ?? [])].sort((a, b) => b.mean_share - a.mean_share),
  );
  protected readonly label = computed<LabelTrend | undefined>(() =>
    this.labels().find((l) => l.label === this.selectedLabel()),
  );
  protected readonly poorlyTracked = computed(() => (this.label()?.tracking_corr ?? 1) < WELL_TRACKED);
  protected readonly topic = computed(() => this.topicData()?.topics.find((t) => t.topic === this.selectedTopic()));

  protected readonly labelSeries = computed<Series[]>(() => {
    const l = this.label();
    return l
      ? [
          { name: 'true labels', color: '#9fb3c8', values: l.true_share },
          { name: 'model prediction', color: '#0f62a8', values: l.predicted_share },
        ]
      : [];
  });
  protected readonly topicSeries = computed<Series[]>(() => {
    const t = this.topic();
    return t ? [{ name: 'share of reports', color: '#0f62a8', values: t.share }] : [];
  });
  protected readonly volumeSeries = computed<Series[]>(() => [
    { name: 'reports per month', color: '#0f62a8', values: this.labelData()?.reports ?? [] },
  ]);
  protected readonly labelsPerReportSeries = computed<Series[]>(() => [
    { name: 'labels per report', color: '#0f62a8', values: this.labelData()?.labels_per_report ?? [] },
  ]);

  constructor() {
    this.triage.labelTrends().subscribe({
      next: (data) => {
        this.labelData.set(data);
        const first = [...data.labels].sort((a, b) => b.mean_share - a.mean_share).find((l) => l.tracking_corr >= 0.85);
        this.selectedLabel.set((first ?? data.labels[0]).label);
      },
      error: () => this.error.set('Could not load trend data. Is the API running and are the trend results generated?'),
    });
    this.triage.topicTrends().subscribe({
      next: (data) => {
        this.topicData.set(data);
        const mask = data.topics.find((t) => t.words.startsWith('mask'));
        this.selectedTopic.set((mask ?? data.topics[0]).topic);
      },
      error: () => this.error.set('Could not load trend data. Is the API running and are the trend results generated?'),
    });
  }

  protected pick(event: Event, target: 'label' | 'topic'): void {
    const value = (event.target as HTMLSelectElement).value;
    if (target === 'label') this.selectedLabel.set(value);
    else this.selectedTopic.set(Number(value));
  }
}
