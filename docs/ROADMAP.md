# Development roadmap

English | [한국어](ROADMAP.ko.md)

## Checklist

- [x] Use a Galaxy Watch as a remote controller
- [x] Set up wireless ADB
- [x] Set up AnExplorer for file management
- [ ] Develop a PDF viewer
- [ ] Develop a GPT viewer
- [ ] Develop C/NDK modules
- [ ] Add smartphone integration
- [ ] Measure memory usage, latency and power consumption
- [ ] Explore camera and AI applications

The list follows the project's public progress summary. Unchecked viewer work includes improving existing prototypes; it does not mean no code exists. AnExplorer's trial is not a guarantee of ongoing free transfer.

## Next verification

| Area | Evidence today | Next step |
|---|---|---|
| Development connection | Helper and wireless ADB verified on the glasses | Reconnection/reboot and changing endpoints |
| Watch input | Galaxy Watch7 / WearMouse remote input established | Per-app click, navigation and Back behavior |
| File management | AnExplorer installed; file permission setup confirmed | Confirm post-trial limits or select an alternative |
| PDF Viewer | Actual document rendering confirmed | Reading UI, direct-original access, navigation and resource cleanup |
| GPT Viewer | Java sample-response prototype builds | Device display/input, then real response delivery |
| Performance | Templates available; no controlled baseline | Measure a baseline and repeat throughout development |
| C processing | Not implemented | Choose a useful workload; define NDK/JNI, buffer and thread boundaries |
| Phone / AI | Not implemented | Verify supported public contracts; start with mock data |
| Camera / AI | Not implemented | Verify permissions, frame/resource lifetime and processing location |

Make one change at a time and separate source, build and device evidence. Keep private papers, conversations and keys out of Git. Existing ChatGPT conversations are separate from application API requests.
