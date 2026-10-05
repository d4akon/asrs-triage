import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { App } from './app';
import { API_URL } from './config';
import { EXAMPLES } from './examples';
import { LabelTrends, PredictResponse, TopicTrends } from './models';

const RESPONSE: PredictResponse = {
  model: 'test-model',
  anomaly: [
    { label: 'Ground Excursion Runway', score: 0.64, predicted: true, terms: ['runway', 'excursion'] },
    { label: 'Aircraft Equipment Problem Critical', score: 0.42, predicted: false, terms: [] },
  ],
  primary_problem: [{ label: 'Human Factors', score: 0.12, predicted: true, terms: [] }],
  similar: [
    {
      acn: '1234567',
      date: '202008',
      similarity: 0.31,
      anomaly: ['Ground Excursion Runway'],
      primary_problem: 'Human Factors',
      snippet: 'We left the runway surface',
    },
  ],
};

const LABEL_TRENDS: LabelTrends = {
  months: ['2020-01', '2020-02', '2020-03'],
  reports: [400, 300, 250],
  labels_per_report: [2.5, 2.5, 2.6],
  labels: [
    {
      label: 'Conflict NMAC',
      mean_share: 0.08,
      tracking_corr: 0.95,
      true_share: [0.05, 0.06, 0.07],
      predicted_share: [0.05, 0.06, 0.08],
      change_points: ['2020-02'],
    },
  ],
};

const TOPIC_TRENDS: TopicTrends = {
  months: ['2020-01', '2020-02', '2020-03'],
  topics: [{ topic: 10, words: 'mask, passenger, wearing', count: 431, share: [0, 0, 0.03] }],
};

describe('App', () => {
  let fixture: ComponentFixture<App>;
  let http: HttpTestingController;
  let page: HTMLElement;

  const submit = () => page.querySelector<HTMLButtonElement>('.submit')!;

  async function type(value: string): Promise<void> {
    const textarea = page.querySelector<HTMLTextAreaElement>('textarea')!;
    textarea.value = value;
    textarea.dispatchEvent(new Event('input'));
    await fixture.whenStable();
  }

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
    fixture = TestBed.createComponent(App);
    http = TestBed.inject(HttpTestingController);
    page = fixture.nativeElement as HTMLElement;
    await fixture.whenStable();
  });

  it('keeps submit disabled until the report is long enough', async () => {
    expect(submit().disabled).toBe(true);
    await type('too short');
    expect(submit().disabled).toBe(true);
    await type('x'.repeat(30));
    expect(submit().disabled).toBe(false);
  });

  it('fills the text area from an example button', async () => {
    page.querySelectorAll<HTMLButtonElement>('.example')[1].click();
    await fixture.whenStable();
    expect(page.querySelector<HTMLTextAreaElement>('textarea')!.value).toBe(EXAMPLES[1].text);
    expect(submit().disabled).toBe(false);
  });

  it('posts the report and renders the returned scores', async () => {
    await type('x'.repeat(30));
    submit().click();
    const request = http.expectOne(`${API_URL}/predict`);
    expect(request.request.body).toEqual({ text: 'x'.repeat(30) });
    request.flush(RESPONSE);
    await fixture.whenStable();

    const labels = Array.from(page.querySelectorAll('.label')).map((el) => el.textContent?.trim());
    expect(labels).toEqual([
      'Ground Excursion Runway',
      'Aircraft Equipment Problem Critical',
      'Human Factors',
    ]);
    expect(page.querySelectorAll('.badge').length).toBe(2);
    expect(page.textContent).toContain('64%');
    expect(page.querySelector('.terms')?.textContent).toContain('runway, excursion');
    expect(page.querySelector('.similar')?.textContent).toContain('ACN 1234567');
    expect(page.querySelector('.similar')?.textContent).toContain('2020-08');
  });

  it('shows the trends view with a label chart and a warning when prediction tracks poorly', async () => {
    page.querySelectorAll<HTMLButtonElement>('.views button')[1].click();
    await fixture.whenStable();
    http.expectOne(`${API_URL}/trends/labels`).flush(LABEL_TRENDS);
    http.expectOne(`${API_URL}/trends/topics`).flush(TOPIC_TRENDS);
    await fixture.whenStable();

    expect(page.querySelector<HTMLSelectElement>('select')!.value).toBe('Conflict NMAC');
    expect(page.querySelectorAll('app-line-chart').length).toBe(3);
    expect(page.querySelector('.muted')?.textContent).toContain('follows this label well');
  });

  it('shows an error when the API cannot be reached', async () => {
    await type('x'.repeat(30));
    submit().click();
    http.expectOne(`${API_URL}/predict`).error(new ProgressEvent('error'));
    await fixture.whenStable();
    expect(page.querySelector('.error')?.textContent).toContain('Cannot reach the API');
    expect(page.querySelector('.results')).toBeNull();
  });
});
