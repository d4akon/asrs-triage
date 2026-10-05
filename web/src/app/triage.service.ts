import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { API_URL } from './config';
import { LabelTrends, PredictRequest, PredictResponse, TopicTrends } from './models';

@Injectable({ providedIn: 'root' })
export class TriageService {
  private readonly http = inject(HttpClient);

  predict(text: string): Observable<PredictResponse> {
    const body: PredictRequest = { text };
    return this.http.post<PredictResponse>(`${API_URL}/predict`, body);
  }

  labelTrends(): Observable<LabelTrends> {
    return this.http.get<LabelTrends>(`${API_URL}/trends/labels`);
  }

  topicTrends(): Observable<TopicTrends> {
    return this.http.get<TopicTrends>(`${API_URL}/trends/topics`);
  }
}
