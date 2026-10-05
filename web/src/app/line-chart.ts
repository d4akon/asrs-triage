import { Component, computed, input } from '@angular/core';

export interface Series {
  name: string;
  color: string;
  values: number[];
}

const WIDTH = 640;
const HEIGHT = 220;
const PAD = { left: 46, right: 12, top: 12, bottom: 28 };

@Component({
  selector: 'app-line-chart',
  template: `
    <svg [attr.viewBox]="'0 0 ' + width + ' ' + height" role="img" [attr.aria-label]="title()">
      @if (bandRange(); as band) {
        <rect class="band" [attr.x]="band.x1" [attr.y]="top" [attr.width]="band.x2 - band.x1" [attr.height]="plotHeight" />
      }
      @for (tick of yTicks(); track tick.label) {
        <line class="grid" [attr.x1]="left" [attr.x2]="width - right" [attr.y1]="tick.y" [attr.y2]="tick.y" />
        <text class="tick" [attr.x]="left - 6" [attr.y]="tick.y + 4" text-anchor="end">{{ tick.label }}</text>
      }
      @for (tick of xTicks(); track tick.label) {
        <text class="tick" [attr.x]="tick.x" [attr.y]="height - 8" text-anchor="middle">{{ tick.label }}</text>
      }
      @for (x of markerXs(); track x) {
        <line class="marker" [attr.x1]="x" [attr.x2]="x" [attr.y1]="top" [attr.y2]="top + plotHeight" />
      }
      @for (line of lines(); track line.name) {
        <path [attr.d]="line.path" fill="none" [attr.stroke]="line.color" stroke-width="2" />
      }
    </svg>
    <div class="legend">
      @for (line of lines(); track line.name) {
        <span><i [style.background]="line.color"></i>{{ line.name }}</span>
      }
      @if (markers().length > 0) {
        <span><i class="dash"></i>detected change point</span>
      }
      @if (band()) {
        <span><i class="swatch"></i>March to May 2020</span>
      }
    </div>
  `,
  styles: `
    svg {
      width: 100%;
      height: auto;
    }
    .grid {
      stroke: #e4e9ee;
    }
    .tick {
      fill: #52606d;
      font-size: 11px;
    }
    .marker {
      stroke: #c0392b;
      stroke-dasharray: 4 3;
    }
    .band {
      fill: #f5a623;
      opacity: 0.18;
    }
    .legend {
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      font-size: 0.85rem;
      color: #52606d;
    }
    .legend i {
      display: inline-block;
      width: 0.9rem;
      height: 0.3rem;
      margin-right: 0.35rem;
      vertical-align: middle;
    }
    .legend i.dash {
      height: 0;
      border-top: 2px dashed #c0392b;
    }
    .legend i.swatch {
      height: 0.7rem;
      background: #f5a623;
      opacity: 0.4;
    }
  `,
})
export class LineChart {
  readonly title = input.required<string>();
  readonly months = input.required<string[]>();
  readonly series = input.required<Series[]>();
  readonly markers = input<string[]>([]);
  readonly band = input<{ from: string; to: string } | null>(null);
  readonly percent = input(false);

  protected readonly width = WIDTH;
  protected readonly height = HEIGHT;
  protected readonly left = PAD.left;
  protected readonly right = PAD.right;
  protected readonly top = PAD.top;
  protected readonly plotHeight = HEIGHT - PAD.top - PAD.bottom;

  private readonly max = computed(() => {
    const peak = Math.max(...this.series().flatMap((s) => s.values), 0);
    return peak > 0 ? peak * 1.1 : 1;
  });

  private x(index: number): number {
    const span = Math.max(this.months().length - 1, 1);
    return PAD.left + (index / span) * (WIDTH - PAD.left - PAD.right);
  }

  private y(value: number): number {
    return PAD.top + this.plotHeight * (1 - value / this.max());
  }

  private format(value: number): string {
    return this.percent() ? `${Math.round(value * 100)}%` : `${Math.round(value * 10) / 10}`;
  }

  protected readonly lines = computed(() =>
    this.series().map((s) => ({
      name: s.name,
      color: s.color,
      path: s.values.map((v, i) => `${i === 0 ? 'M' : 'L'}${this.x(i).toFixed(1)},${this.y(v).toFixed(1)}`).join(' '),
    })),
  );

  protected readonly yTicks = computed(() =>
    [0, 0.5, 1].map((f) => ({ label: this.format(this.max() * f), y: this.y(this.max() * f) })),
  );

  protected readonly xTicks = computed(() =>
    this.months()
      .map((m, i) => ({ label: m, x: this.x(i) }))
      .filter((_, i) => i % 6 === 0),
  );

  protected readonly markerXs = computed(() =>
    this.markers()
      .map((m) => this.months().indexOf(m))
      .filter((i) => i >= 0)
      .map((i) => this.x(i)),
  );

  protected readonly bandRange = computed(() => {
    const band = this.band();
    if (!band) return null;
    const from = this.months().indexOf(band.from);
    const to = this.months().indexOf(band.to);
    return from < 0 || to < 0 ? null : { x1: this.x(from), x2: this.x(to) };
  });
}
