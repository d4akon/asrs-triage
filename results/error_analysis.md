# Error analysis (run 7, test set)

Exact-match accuracy over all anomaly labels: transformer 0.075, baseline 0.124

Labels per report: true mean 3.13, transformer predicts 2.58

## Per-label F1 (sorted by test support)

| label                                                             |   support |   transformer |   baseline |   diff |
|:------------------------------------------------------------------|----------:|--------------:|-----------:|-------:|
| Deviation / Discrepancy - Procedural Published Material / Policy  |      1909 |         0.589 |      0.664 | -0.075 |
| Aircraft Equipment Problem Critical                               |       852 |         0.695 |      0.71  | -0.015 |
| Deviation / Discrepancy - Procedural Clearance                    |       789 |         0.429 |      0.506 | -0.077 |
| Deviation / Discrepancy - Procedural FAR                          |       645 |         0.194 |      0.208 | -0.014 |
| Aircraft Equipment Problem Less Severe                            |       508 |         0.361 |      0.418 | -0.057 |
| ATC Issue All Types                                               |       470 |         0.649 |      0.732 | -0.084 |
| Conflict NMAC                                                     |       386 |         0.777 |      0.829 | -0.052 |
| Inflight Event / Encounter CFTT / CFIT                            |       313 |         0.723 |      0.852 | -0.128 |
| Deviation / Discrepancy - Procedural Maintenance                  |       248 |         0.618 |      0.543 |  0.076 |
| Inflight Event / Encounter Weather / Turbulence                   |       246 |         0.65  |      0.659 | -0.009 |
| Deviation - Altitude Excursion From Assigned Altitude             |       233 |         0.315 |      0.329 | -0.014 |
| Flight Deck / Cabin / Aircraft Event Smoke / Fire / Fumes / Odor  |       229 |         0.849 |      0.897 | -0.048 |
| Deviation - Track / Heading All Types                             |       205 |         0.243 |      0.486 | -0.243 |
| Conflict Ground Conflict                                          |       200 |         0.655 |      0.766 | -0.111 |
| Airspace Violation All Types                                      |       167 |         0.359 |      0.486 | -0.127 |
| Critical                                                          |       164 |         0.628 |      0.672 | -0.043 |
| Ground Event / Encounter Loss Of Aircraft Control                 |       156 |         0.68  |      0.765 | -0.085 |
| Deviation / Discrepancy - Procedural Hazardous Material Violation |       152 |         0.842 |      0.914 | -0.072 |
| Conflict Airborne Conflict                                        |       119 |         0.349 |      0.48  | -0.131 |
| Inflight Event / Encounter Loss Of Aircraft Control               |       106 |         0.378 |      0.281 |  0.097 |
| Deviation - Altitude Overshoot                                    |        94 |         0.339 |      0.348 | -0.009 |
| Inflight Event / Encounter Unstabilized Approach                  |        93 |         0.312 |      0.444 | -0.133 |
| Deviation / Discrepancy - Procedural Weight And Balance           |        92 |         0.267 |      0.365 | -0.098 |
| Ground Event / Encounter Other / Unknown                          |        90 |         0.231 |      0.139 |  0.092 |
| Ground Excursion Runway                                           |        88 |         0.579 |      0.798 | -0.219 |
| Deviation / Discrepancy - Procedural MEL / CDL                    |        86 |         0.605 |      0.549 |  0.056 |
| Inflight Event / Encounter Fuel Issue                             |        84 |         0.476 |      0.761 | -0.285 |
| Inflight Event / Encounter Wake Vortex Encounter                  |        74 |         0.814 |      0.882 | -0.067 |
| Deviation - Speed All Types                                       |        73 |         0.301 |      0.552 | -0.25  |
| Flight Deck / Cabin / Aircraft Event Illness / Injury             |        65 |         0.408 |      0.544 | -0.136 |
| Ground Incursion Runway                                           |        65 |         0.361 |      0.532 | -0.171 |
| Ground Incursion Taxiway                                          |        55 |         0.449 |      0.529 | -0.081 |
| Ground Event / Encounter Ground Strike - Aircraft                 |        55 |         0.374 |      0.553 | -0.179 |
| Flight Deck / Cabin / Aircraft Event Other / Unknown              |        50 |         0.068 |      0.109 | -0.041 |
| Deviation - Altitude Crossing Restriction Not Met                 |        44 |         0.234 |      0.435 | -0.201 |
| Inflight Event / Encounter Other / Unknown                        |        38 |         0.113 |      0.12  | -0.007 |
| Less Severe                                                       |        37 |         0.18  |      0.218 | -0.038 |
| Ground Event / Encounter Object                                   |        34 |         0.234 |      0.205 |  0.029 |
| Ground Event / Encounter Vehicle                                  |        24 |         0.222 |      0.08  |  0.142 |
| Deviation - Altitude Undershoot                                   |        21 |         0.138 |      0.091 |  0.047 |
| Flight Deck / Cabin / Aircraft Event Passenger Misconduct         |        14 |         0.364 |      0.421 | -0.057 |
| Inflight Event / Encounter Bird / Animal                          |        12 |         0.24  |      0.4   | -0.16  |
| Ground Event / Encounter Aircraft                                 |        11 |         0.08  |      0     |  0.08  |
| Inflight Event / Encounter Object                                 |        11 |         0.163 |      0     |  0.163 |
| Ground Event / Encounter Person / Animal / Bird                   |        11 |         0.316 |      0     |  0.316 |
| Ground Event / Encounter Gear Up Landing                          |        10 |         0.222 |      0     |  0.222 |
| Inflight Event / Encounter VFR In IMC                             |         9 |         0.194 |      0     |  0.194 |
| Flight Deck / Cabin / Aircraft Event Passenger Electronic Device  |         9 |         0.267 |      0     |  0.267 |
| Ground Excursion Taxiway                                          |         9 |         0.211 |      0     |  0.211 |
| Deviation / Discrepancy - Procedural Other / Unknown              |         9 |         0.065 |      0     |  0.065 |
| Deviation / Discrepancy - Procedural Security                     |         4 |         0.095 |      0     |  0.095 |
| Deviation / Discrepancy - Procedural Landing Without Clearance    |         4 |         0     |      0     |  0     |
| No Specific Anomaly Occurred All Types                            |         2 |         0     |      0     |  0     |

## Exact-match by report length (words, quartiles)

| len             |   transformer |   baseline |
|:----------------|--------------:|-----------:|
| (4.999, 121.5]  |         0.095 |      0.155 |
| (121.5, 216.0]  |         0.082 |      0.123 |
| (216.0, 377.0]  |         0.077 |      0.133 |
| (377.0, 3594.0] |         0.045 |      0.085 |

Reports likely over the 512-token limit (>384 words): 24.0% of test

## Most common Primary Problem confusions (true -> predicted)

- 137x  Procedure -> Human Factors
- 69x  Human Factors -> Procedure
- 51x  Human Factors -> Ambiguous
- 51x  Aircraft -> Human Factors
- 44x  Ambiguous -> Human Factors
- 42x  Human Factors -> Aircraft
- 33x  Human Factors -> Airspace Structure
- 29x  Human Factors -> Environment - Non Weather Related
- 27x  Human Factors -> Weather
- 26x  Environment - Non Weather Related -> Human Factors

## 20 random misclassified reports

### acn 1862007 (197 words)
- true: ['Aircraft Equipment Problem Critical', 'Inflight Event / Encounter Loss Of Aircraft Control']
- predicted: ['Conflict NMAC', 'Inflight Event / Encounter Object', 'Inflight Event / Encounter Other / Unknown']
- text: I got authorization to fly recreationally. I was in a nice cruise down a trail while maintaining visual [line] of sight when the drone made a hard right turn into a tree. The drone had acted up near that spot by coming to a slow stop and about 600 feet later did the same thing. All sensors were turned off and the flight was in sports mode. No one or property was injured in the accident except for my props. The drone flight data shows the drone made a hard right turn into the trees while the stick was pointed to the left. I believe that local interference caused my drone to turn and crash into the trees. There is at least one tower with a microwave transmitter near by; along with the Water Tr

### acn 1824212 (105 words)
- true: ['Deviation / Discrepancy - Procedural Hazardous Material Violation', 'Deviation / Discrepancy - Procedural Published Material / Policy']
- predicted: ['Deviation / Discrepancy - Procedural Hazardous Material Violation', 'Deviation / Discrepancy - Procedural Published Material / Policy', 'Deviation / Discrepancy - Procedural Weight And Balance']
- text: I was advised by Person X that I had loaded an unidentified Hazmat parcel on Aircraft X with no NOTOC. I was the only one involved.Apparently; the event occurred because I supposedly loaded a Hazmat PPS without a NOTOC on Aircraft X. After discussing this with a manager I went back in the NOTOC System and saw no NOTOC was planned for that flight for that date.Once the event was identified even though it was exactly a week later; I spoke with the manager and advised him I was filling out a report.Suggestion - Double checking boxes for DG labels [since no NOTOC was issued].

### acn 1821703 (181 words)
- true: ['Aircraft Equipment Problem Less Severe', 'Deviation / Discrepancy - Procedural FAR', 'Deviation / Discrepancy - Procedural MEL / CDL', 'Deviation / Discrepancy - Procedural Published Material / Policy', 'Flight Deck / Cabin / Aircraft Event Illness / Injury']
- predicted: ['Aircraft Equipment Problem Less Severe', 'Deviation / Discrepancy - Procedural MEL / CDL']
- text: During taxi out the APU on the aircraft failed with only one engine running. We then returned to the gate and the captain requested all passengers deplane while we waited for the MEL for the APU because the cabin temperature was becoming extremely unsafe. An air cart was attached to the aircraft because the bridge air was not cooling the aircraft; but this did not make a significant impact on the cabin temperature. We reboarded the aircraft and pushed back; but due to the remnants of Tropical Storm Name; there were significant departure delays and we need up with a 64 minute taxi-out. After we were airborne FA4 asked the Captain what the cabin temperature reached while we were waiting for de

### acn 1863383 (50 words)
- true: ['Aircraft Equipment Problem Less Severe', 'Deviation / Discrepancy - Procedural Published Material / Policy']
- predicted: ['Aircraft Equipment Problem Critical']
- text: In position and hold with park brake set; master caution; followed by L ENG failure and L ENG fuel valve EICAS. Ran checklist and returned to gate. While in position and hold; idle power. Left engine failed; we had a MEL XX-XX not sure MEL had any bearing on event.

### acn 1837391 (87 words)
- true: ['Ground Event / Encounter Other / Unknown']
- predicted: ['Ground Event / Encounter Other / Unknown', 'No Specific Anomaly Occurred All Types']
- text: There is ongoing Taxiway construction on A adjacent to the Terminal. The NOTAMs mention closure of the Taxiway but there is no mention of the work on [the] airline ramp. There needs to be a NOTAM to reflect the ramp construction. The construction goes far beyond Taxiway A and there needs to be a NOTAM that if you are parking gates 1; 2; 3; 4; 6; that they should only be accessed via A10; A then A9. I feel this is a grave hazard to our operation.

### acn 1842906 (12 words)
- true: ['Deviation / Discrepancy - Procedural FAR', 'Deviation / Discrepancy - Procedural Hazardous Material Violation', 'Deviation / Discrepancy - Procedural Published Material / Policy']
- predicted: ['Deviation / Discrepancy - Procedural Hazardous Material Violation', 'Deviation / Discrepancy - Procedural Maintenance', 'Deviation / Discrepancy - Procedural Published Material / Policy']
- text: Collapsible Scooter / Wheelchair - Lithium Battery Not Removed per FAA requirement.

### acn 1840278 (318 words)
- true: ['Conflict NMAC', 'Deviation / Discrepancy - Procedural Published Material / Policy']
- predicted: ['Conflict NMAC']
- text: I was returning from a pleasure flight from [ANON] to my home airport [ANON] and had joined Runway XX right downwind via the right 45. I had made all my radio calls: joining the right 45 Runway XX; established on the right 45 Runway XX; Right downwind XX; Right downwind abeam XX numbers. There were at least 2 other aircraft in the pattern and my pattern entry was quite seamless - I was careful to maintain the headings and altitudes - and monitor every other plane's position both on ADS-B and visually. Frankly; I think I did a very good job. As I was turning base; I made my radio call ('turning right base Runway XX') then I saw ***RIGHT IN FRONT ON ME***; at 11 o'clock; a Cessna 172 convergin

### acn 1865380 (118 words)
- true: ['Airspace Violation All Types', 'Conflict Airborne Conflict', 'Deviation / Discrepancy - Procedural FAR', 'Deviation / Discrepancy - Procedural Published Material / Policy', 'Inflight Event / Encounter Object']
- predicted: ['Conflict NMAC']
- text: At the FAF on Runway 28R in SFO; the pilots noticed a small drone at our 2 o' clock position for about 1 or 2 seconds. The drone appeared black in color and had no lights. It was dark out and at first the pilots thought it was a bird but then determined it was man made. The aircraft lighting made us able to spot the drone on approach. Could not determine direction; speed or if hovering. SFO 28L approach; just prior to sundown and descending through approx 1400 ft. AGL a black drone with no lights passed just outside the right wing. This was not a small toy UAV. We reported the sighting to Tower and landed.

### acn 1843669 (89 words)
- true: ['Deviation - Track / Heading All Types', 'Deviation / Discrepancy - Procedural Clearance', 'Inflight Event / Encounter Wake Vortex Encounter']
- predicted: ['Deviation - Altitude Excursion From Assigned Altitude', 'Deviation - Speed All Types', 'Inflight Event / Encounter Loss Of Aircraft Control', 'Inflight Event / Encounter Wake Vortex Encounter']
- text: During takeoff/climbout (200') we entered wake turbulence from a 757 in front of us. The aircraft rolled to the right and we continued to climb just to the right of course. (0.18 was shown on the MFD). Winds were 150/07 and we were LNAV to RONII. Before getting back on LNAV track; ATC assigned us to a left turn to 070 and stated we were south of our track. In the next transmission; we stated what had happened (wake turbulence) and the Controller cleared us to continue the departure.

### acn 1845121 (531 words)
- true: ['Deviation / Discrepancy - Procedural Published Material / Policy']
- predicted: ['Deviation / Discrepancy - Procedural Published Material / Policy', 'Flight Deck / Cabin / Aircraft Event Illness / Injury']
- text: It has come to my attention that a great many Pilots and Flight Attendants are operating an aircraft under a climate of increased stress and decreased quality of life due to recent COVID-19 vaccine mandates.Never before; at any time in my career; have I witnessed a more divisive and disruptive workplace issue as is this particular mandate.Civilian Pilots in the United States are presently operating thousands of aircraft; and managing the well-being of millions of passengers; with what is essentially a proverbial gun held to our heads. The timer is running out. The pressure is increasing every single day.To quote a pilot I spoke with earlier this week; 'I'm having difficulty sleeping...anythi

### acn 1814508 (614 words)
- true: ['Aircraft Equipment Problem Less Severe']
- predicted: ['Aircraft Equipment Problem Critical']
- text: Climbing on the SID the forward Flight Attendant called the flight deck about noise coming from the main cabin door. We verified that the doors indications were all closed. No pressurization abnormalities were noted with the CPAM system. The noise was not audible in the flight deck. Shortly after the Flight Attendant called again saying the noise was louder; at which time the CPAM and doors EICAS (Engine Indicating and Crew Alerting System) page indications were checked again. Pilot Monitoring advised the Flight Attendant to verify all door securing pins were in the green position and to try and detect if air was passing through. During this time ATC amended our climb instructions from 37;00

### acn 1855165 (93 words)
- true: ['Aircraft Equipment Problem Less Severe', 'Deviation / Discrepancy - Procedural Published Material / Policy']
- predicted: ['Aircraft Equipment Problem Less Severe', 'Inflight Event / Encounter Other / Unknown']
- text: I got an erroneous indication on the cockpit display then a complete loss of GPS signal. After several attempts to regain a signal and be able to navigate to the next Waypoint; I had to ask Center for a heading till I sorted out the issues. Finally after several minutes I was able to get a distance Waypoint and able to navigate to that intersection and no further issues happened. This happened near the area of Restricted airspace R-[ANON] past [ANON]. Looking back; I'm convinced my GPS signal was jammed by the military.

### acn 1843594 (153 words)
- true: ['Aircraft Equipment Problem Critical', 'Deviation / Discrepancy - Procedural Clearance']
- predicted: ['Aircraft Equipment Problem Critical', 'Aircraft Equipment Problem Less Severe']
- text: 900 miles out of [ANON]; just past [ANON]. We received ATA Fail> AUNX MAU (Master Avionics Unit) 3A Fail. ADS 3 Fail. Spoiler Fault. FDR AFT Fail. Auto Config Trim FailAll nav indications on the FO (First Officer) side is gone. Flight director is gone. Auto throttle disengaged and auto pilot disengaged. We performed QRH for the AUNX (Annunciator Message). We found that we have lost systems and flight controls; i.e. multi-functional spoilers and speed brakes. In addition we were not for sure if we had lost OB brakes...no indication on the status page. This concerned us given; #2 OB locked up on validation flight. We made a crew decision to turn back for [ANON]. Once it was decided we were tur

### acn 1805583 (184 words)
- true: ['ATC Issue All Types', 'Inflight Event / Encounter Loss Of Aircraft Control', 'Inflight Event / Encounter Wake Vortex Encounter']
- predicted: ['Inflight Event / Encounter Loss Of Aircraft Control', 'Inflight Event / Encounter Wake Vortex Encounter']
- text: Departing DTW [Runway] 3L on the HHOWE3 RNAV departure we had a wake turbulence encounter.  ATC cleared us for takeoff behind an A320. We completed a normal takeoff profile.  Autopilot was engaged at 600 feet AGL and flap retraction was completed on schedule.  We were at approximately 1;800 feet AGL (2;450 feet MSL) accelerating when the aircraft abruptly rolled 35 degrees right and pitched up. The autopilot disconnected automatically and the shaker activated momentarily for around 1-2 seconds.  Having a hand defensively positioned for the yoke; I immediately pitched down and rolled the wings level.  Once the aircraft was sufficiently under control and at a safe airspeed; autopilot was reeng

### acn 1839380 (191 words)
- true: ['Aircraft Equipment Problem Critical', 'Inflight Event / Encounter Loss Of Aircraft Control']
- predicted: []
- text: My student and I departed southwest from [ANON] on a mini cross country. When I took the controls so my student could get his charts out (approximately 7 miles away from the airport); I noticed that the trim wheel could only be progressively moved in the nose down position. At some point I had to apply quite a lot of yoke aft pressure to keep the plane in straight and level flight. I made a 180; and let ATC know the situation. On the way back for landing; my student appeared to have forced the nose trim wheel downwards in order to get some nose up trim action and we heard a loud snapping or cracking noise. After the noise; the trim wheel operated normally; and we were able to fly the plane n

### acn 1809084 (194 words)
- true: ['Airspace Violation All Types', 'Conflict NMAC', 'Deviation / Discrepancy - Procedural FAR', 'Deviation / Discrepancy - Procedural Published Material / Policy']
- predicted: ['Conflict Airborne Conflict', 'Conflict NMAC', 'Inflight Event / Encounter Other / Unknown']
- text: Flew Korry 4 arrival and proceeding visually up the Hudson River at 4;000 feet. Cleared to descend to 3;000 feet. Descending out of 3;500 feet about abeam the museum; noticed an object at our 12 o'clock; flying very stable; and appeared to be flying towards us; at the time our speed was 250 knots. We made no corrective action with our aircraft and continued on descent and heading as there was very little time for it to come and go. It passed approximately 100 feet under the aircraft and was flat oval in shape and a very shiny black in color. I have seen many Mylar Balloons and it definitely wasn't one of them. It had the appearance and actions of a DRONE. We immediately reported it to Air Tr

### acn 1857302 (391 words)
- true: ['Flight Deck / Cabin / Aircraft Event Illness / Injury', 'Inflight Event / Encounter Weather / Turbulence']
- predicted: ['Deviation / Discrepancy - Procedural Published Material / Policy', 'Inflight Event / Encounter Weather / Turbulence', 'No Specific Anomaly Occurred All Types']
- text: 1st day; scheduled [ANON]-[ANON]-[ANON] (XA:21 scheduled block). Fully into winter ops now. Scheduled arrival [ANON] time XP:31. Late fuel in [ANON]. Late push. Strong headwinds to [ANON]. At gate in [ANON] at XP:58 local. Both of us were yawning and eye rubbing halfway through our 6+ hour flight. On final approach; had trouble focusing and keeping scan congruent. Was difficult to plan and arrive on a stable; timely profile. At the FAF; encountered unexpected shifting winds & moderate turbulence. This required extra vigilance to avoid exceedance. I had gotten appropriate; average sleep the night before. I was hydrated and consumed caffeine drinks throughout the flight. Despite all this prepa

### acn 1836832 (349 words)
- true: ['Aircraft Equipment Problem Critical']
- predicted: ['Aircraft Equipment Problem Critical', 'Inflight Event / Encounter Fuel Issue']
- text: During flight on a practice VFR/VMC approach; the engine began sputtering. I swapped fuel tanks and it fixed the issue but I immediately began making my way to the nearest airport ([ANON] about 10NM from our location). Roughly 5-10 seconds later; the engine began sputtering again. I swapped the tanks again; and identified a location to set it down. A few seconds after swapping fuel tanks for the second time the engine quit. The auxiliary pump was on before the first instance of engine sputter and remained for the remainder of the flight. Once the engine quit and I realized I was not going to make [ANON]; so I [advised ATC] on XXX.YYY ([ANON] Approach). I advised Approach I was over the town 

### acn 1851021 (1689 words)
- true: ['Aircraft Equipment Problem Less Severe', 'Deviation - Speed All Types', 'Deviation / Discrepancy - Procedural FAR', 'Deviation / Discrepancy - Procedural Maintenance', 'Deviation / Discrepancy - Procedural Published Material / Policy']
- predicted: ['Aircraft Equipment Problem Less Severe', 'Deviation / Discrepancy - Procedural Published Material / Policy']
- text: Flight XXXX scheduled as an empty ferry flight [ANON]-[ANON] diverted into [ANON] after an Airspeed Disagree on takeoff.This pairing was originally built as a day trip deadhead to [ANON]; fly to [ANON]. After determining that the appropriate parts had not yet been sent to [ANON]; we were reassigned to a two day with two short rest overnights. This created a fatigue management threat. I slept well after my day trip ; slept virtually the entire flight down and multiple hours in the afternoon. Though my sleep was separated into multiple longer segments; I felt rested for the flight.In this narrative; I am the Pilot Flying until after exiting the hold and commencing the approach. On the van driv

### acn 1807149 (255 words)
- true: ['Conflict NMAC']
- predicted: ['ATC Issue All Types', 'Conflict NMAC']
- text: While descending into [ANON]; my student elected to make a midfield entry into the downwind. We briefed the approach and announced our position on CTAF at about 4 miles outside of the airport. Following our call; another aircraft asked our location in relation to the airport. We attempted to reply; but severe radio congestion prevented a response. The student and I began scanning for traffic; but it appeared that no other aircraft were in our area. Just after crossing midfield; we began our turn to downwind when the previous aircraft announced a midfield downwind. We spotted the traffic 100 to 150 feet below us and passing underneath us to our left. We took evasive action and initiated a cli
