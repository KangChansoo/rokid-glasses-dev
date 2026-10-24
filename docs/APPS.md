# Apps and installation

English | [한국어](APPS.ko.md)

| App | Package | Output |
|---|---|---|
| Rokid ADB Helper | dev.rokidapps.adbhelper | dist/adb-helper-android-debug.apk |
| GPT Viewer APK | dev.rokidapps.gptviewer | dist/gpt-viewer-android-debug.apk |
| Paper Viewer APK | dev.rokidapps.paperviewer | dist/paper-viewer-android-debug.apk |

Install on the glasses through Hi Rokid Toolbox, or use ADB with an explicit glasses target. Validate each app's launch, pointer, temple input and Back behavior separately. Current app controls are Korean; English repository docs do not imply an English app UI.

## ADB Helper

Installation, settings access, developer-option activation and PC pairing succeeded on the glasses. Follow the [ADB guide](ADB.md).

## GPT Viewer

The prototype contains Hello World, three handwritten sample-response pages, and Next/Previous/Reset/Exit controls. It has no live OpenAI API connection and cannot read existing ChatGPT conversations. Build checks passed; device display/input validation remains pending.

## Paper Viewer

The app renders original PDF pages using Android PdfRenderer. A real document was displayed on the glasses, as reported by the user and confirmed in a screenshot. Reading comfort, navigation and file handling still need improvement; this is not a finished reader.

Implemented controls include Previous/Next, zoom and pointer dragging/wheel movement. Only one current document is stored. Password-protected PDFs, OCR, search, annotations and a multi-document library are not supported.

### Open a document

1. **데모 (Demo)** creates a synthetic three-page PDF on the device. No real paper is bundled.
2. **PDF 열기 (Open PDF)** launches the Android document picker for a local PDF.
3. A file manager can pass a PDF through **Open with → Paper Viewer APK**, using a readable content URI. A particular source folder is not required. See [file transfer](FILE_TRANSFER.md).
4. **앱 폴더 (App folder)** lists PDFs in the app-owned Documents directory as a fallback.

The fallback directory is `/storage/emulated/0/Android/data/dev.rokidapps.paperviewer/files/Documents/`. File managers may not be able to write there. If neither a picker, a compatible Open with provider nor this directory is usable, document input remains unresolved. Do not add all-files access as an automatic workaround.

### Current copy behavior

Selecting or externally opening a PDF currently copies it to the private `files/current.pdf` and resets the saved page. Reopening the app restores that copy and its page. The source file is not modified. **문서 제거 (Remove document)** removes the internal copy and saved position, not the source.

This simplifies stream compatibility and access lifetime but duplicates storage and adds opening latency. Direct read-only access to the original, document-specific reading positions and limited temporary caching are planned; they have not been implemented. A provider must supply a seekable file descriptor for direct PdfRenderer access. Persistent access cannot be assumed for every Open with URI.

The file limit is 200 MB. Rendering is bounded to four million pixels (approximately 16 MB for the bitmap), a maximum side of 4096 pixels and one worker thread. Backups are disabled.

The device screenshot confirmed PDF content and a 3.2x zoom state, not the full reliability of zoom, panning, input mappings or restoration. These flows, fonts, long documents and power use still need testing. Private documents and screenshots are not published in this repository.

References: [Android PdfRenderer](https://developer.android.com/reference/android/graphics/pdf/PdfRenderer), [document access](https://developer.android.com/training/data-storage/shared/documents-files).
