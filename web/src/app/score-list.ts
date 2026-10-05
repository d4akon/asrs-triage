import { DecimalPipe } from '@angular/common';
import { Component, input } from '@angular/core';

import { LabelScore } from './models';

@Component({
  selector: 'app-score-list',
  imports: [DecimalPipe],
  template: `
    @for (item of items(); track item.label) {
      <div class="row" [class.predicted]="item.predicted">
        <div class="row-head">
          <span class="label">{{ item.label }}</span>
          @if (item.predicted) {
            <span class="badge">predicted</span>
          }
          <span class="score">{{ item.score * 100 | number: '1.0-0' }}%</span>
        </div>
        @if (item.terms.length > 0) {
          <div class="terms">because of: {{ item.terms.join(', ') }}</div>
        }
        <div
          class="bar"
          role="meter"
          [attr.aria-label]="item.label"
          aria-valuemin="0"
          aria-valuemax="1"
          [attr.aria-valuenow]="item.score"
        >
          <div class="fill" [style.width.%]="item.score * 100"></div>
        </div>
      </div>
    }
  `,
  styles: `
    .row {
      margin-bottom: 0.9rem;
    }
    .row-head {
      display: flex;
      align-items: baseline;
      gap: 0.5rem;
    }
    .label {
      flex: 1;
      color: #3d4852;
    }
    .predicted .label {
      color: #0f2a43;
      font-weight: 600;
    }
    .badge {
      background: #0f62a8;
      color: #fff;
      border-radius: 999px;
      padding: 0.05rem 0.55rem;
      font-size: 0.75rem;
    }
    .score {
      min-width: 3rem;
      text-align: right;
      font-variant-numeric: tabular-nums;
      color: #52606d;
    }
    .terms {
      margin-top: 0.15rem;
      font-size: 0.8rem;
      color: #7b8794;
    }
    .bar {
      height: 0.5rem;
      margin-top: 0.3rem;
      background: #e4e9ee;
      border-radius: 999px;
      overflow: hidden;
    }
    .fill {
      height: 100%;
      background: #9fb3c8;
    }
    .predicted .fill {
      background: #0f62a8;
    }
  `,
})
export class ScoreList {
  readonly items = input.required<LabelScore[]>();
}
