import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { App } from './app';
import { API_URL } from './config';
import { EXAMPLES } from './examples';
import { PredictResponse } from './models';

const RESPONSE: PredictResponse = {
  model: 'test-model',
  anomaly: [
    { label: 'Ground Excursion Runway', score: 0.64, predicted: true },
    { label: 'Aircraft Equipment Problem Critical', score: 0.42, predicted: false },
  ],
  primary_problem: [{ label: 'Human Factors', score: 0.12, predicted: true }],
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
