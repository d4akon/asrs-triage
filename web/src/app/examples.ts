export interface Example {
  title: string;
  text: string;
}

export const EXAMPLES: Example[] = [
  {
    title: 'Altitude deviation',
    text:
      'While level at FL350 on a transcontinental flight the autopilot disconnected without warning during a period of moderate turbulence. ' +
      'The aircraft climbed approximately 400 feet before the First Officer, who was flying, took manual control and returned to the assigned altitude. ' +
      'Center called and asked us to verify our altitude, and we advised that we were correcting a deviation caused by the autopilot disconnect. ' +
      'No traffic conflict resulted. We discussed the event and reviewed the autopilot disconnect procedure.',
  },
  {
    title: 'Smoke in the cabin',
    text:
      'During climbout through 8,000 feet the cabin crew reported a strong electrical burning smell in the aft galley. ' +
      'A flight attendant found a galley oven emitting light smoke. The Captain declared an emergency and we followed the smoke and fumes checklist, removing power from the galley bus. ' +
      'The smell dissipated within several minutes. We returned to the departure airport and landed uneventfully with fire crews standing by. ' +
      'Maintenance later found a failed heating element.',
  },
  {
    title: 'Runway excursion',
    text:
      'Landing on a wet runway with a gusty crosswind, the aircraft began drifting left of centerline after touchdown. ' +
      'Despite full rudder and braking inputs the aircraft departed the left side of the runway and stopped in the grass about 50 feet from the edge of the pavement. ' +
      'There were no injuries. Contributing factors were a braking action report that was not updated and my decision to continue the approach with the crosswind component near the limit.',
  },
];
