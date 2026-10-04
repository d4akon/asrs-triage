import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { API_URL } from './config';
import { PredictRequest, PredictResponse } from './models';

@Injectable({ providedIn: 'root' })
export class TriageService {
  private readonly http = inject(HttpClient);

  predict(text: string): Observable<PredictResponse> {
    const body: PredictRequest = { text };
    return this.http.post<PredictResponse>(`${API_URL}/predict`, body);
  }
}
