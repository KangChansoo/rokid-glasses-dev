# Battery measurement checklist

English | [한국어](BATTERY.ko.md)

One short observation of a ten-percentage-point drop cannot establish a defect or normal endurance. Start at 100% and repeat comparable conditions. This experiment does not establish manufacturer-rated or full-discharge lifetime.

## Preparation

- [ ] Charge the glasses, watch and phone; record each starting level.
- [ ] Charge the glasses to 100%, unplug, and distinguish the initial change from a steadier interval.
- [ ] Record model, firmware, Hi Rokid, WearMouse, phone OS and app commit/APK version.
- [ ] Keep brightness, volume, Wi-Fi, Bluetooth peers, temperature and indoor/outdoor conditions consistent.
- [ ] Finish updates/resource downloads/photo/audio/screen recording first, or test them as separate workloads.
- [ ] Use ISO timestamps in Asia/Seoul. If sampling every five minutes, minimize the screen use caused by checking.
- [ ] Measure while stationary, not walking or driving.

## Compare conditions

Where practical, repeat each condition three times for 20–30 minutes at similar charge levels. The gauge may remain at 100% for a while; compare matching charge ranges as well. Allow rest between repeated charging sessions.

| Condition | Display | Watch | Phone / workload | Purpose |
|---|---|---|---|---|
| A | Off / normal standby | Disconnected | Hi Rokid connected, no downloads | Baseline |
| B | Static Hello World | Disconnected | Same | Display contribution |
| C | Same as B | WearMouse connected, idle | Same | Connection maintenance |
| D | Same | Fixed clicks per minute | Same | Input contribution |
| E (future) | CXR-L Custom View | Connected if supported | One static update | SDK-path comparison |
| F (future) | Completed-answer display | Same | Fixed-interval mock requests | Network/update contribution |

Average drain is `(start level - end level) / elapsed hours`, in **percentage points per hour**. Battery percentages are integer, nonlinear estimates: do not extrapolate a five-minute interval into all-day endurance. Report median, range and original durations. Exclude charging intervals from analysis.

## Observations and stopping

- [ ] Separate time from 100 to 90% from later intervals of equal length.
- [ ] Record display on/off, sleep, Bluetooth reconnection and foreground changes.
- [ ] Track Watch7 and phone charge as well as the glasses.
- [ ] Stop if heat, system warnings or unexpected shutdown occurs; follow manufacturer guidance.
- [ ] If rapid drain repeats under comparable conditions, use private measurements when contacting official support. Do not post account information or serial numbers in public issues.

Template: [battery-template.csv](../measurements/battery-template.csv). Store real measurements under ignored `measurements/private/`.
