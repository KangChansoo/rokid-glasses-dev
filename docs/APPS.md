# 앱과 설치

| 앱 | 패키지 | 파일 |
|---|---|---|
| Rokid ADB Helper | dev.rokidapps.adbhelper | dist/adb-helper-android-debug.apk |
| GPT Viewer APK | dev.rokidapps.gptviewer | dist/gpt-viewer-android-debug.apk |
| Paper Viewer APK | dev.rokidapps.paperviewer | dist/paper-viewer-android-debug.apk |

Hi Rokid 도구 상자로 **안경에 설치**합니다. 연결된 안경을 명시한 ADB 설치도 가능합니다. 설치 후 실제 실행 메뉴·포인터·기본 터치·Back 동작은 앱별로 확인합니다.

## ADB Helper

실제 안경에서 설치·기기 정보·개발자 옵션·무선 디버깅 설정과 PC 페어링 성공을 확인했습니다. [전체 절차](ADB.md)를 따릅니다.

## GPT Viewer

Hello World, 한글로 직접 작성한 가상 답변 3장, 다음·이전·처음·종료가 있습니다. 실제 OpenAI API나 기존 ChatGPT 대화는 연결되지 않습니다. 코드와 빌드는 준비됐으나 Viewer의 실기기 표시/입력 확인은 대기입니다.

## Paper Viewer

안경 내부의 PDF 원본 페이지를 Android PdfRenderer로 표시합니다. 그림·수식을 포함한 페이지 렌더링, 이전/다음, 확대, 포인터 드래그/휠을 구현했습니다. 한 문서만 보관하며 암호 PDF/OCR/검색/주석/여러 문서 책장은 지원하지 않습니다.

1. 먼저 `데모`를 실행합니다. 실제 논문 대신 기기에서 직접 만든 가상 PDF 3쪽입니다.
2. 본인 PDF를 안경으로 전송하고 `PDF 열기`의 시스템 파일 선택기로 선택합니다.
3. 선택기가 없으면 `앱 폴더` 버튼으로 앱 소유 Documents 위치를 확인합니다. 해당 위치로 업로드할 수 있는지는 별도 기기 확인이 필요합니다.
4. 파일 관리자에서 `다른 앱으로 열기`를 지원하면 Paper Viewer에 content:// 문서를 전달할 수도 있습니다.

앱 소유 폴더는 `/storage/emulated/0/Android/data/dev.rokidapps.paperviewer/files/Documents/`입니다. 선택기와 해당 폴더 접근이 모두 없다면 파일 입력 경로는 미해결이며 전체 저장소 권한으로 자동 우회하지 않습니다.

선택 PDF는 `files/current.pdf`로 내부 사본 한 부를 만들고 읽던 쪽을 기억합니다. 원본은 변경하지 않습니다. `문서 제거`는 내부 사본과 위치만 지웁니다. 백업은 비활성화합니다. 입력 200MB, 렌더링 최대 4백만 픽셀/약 16MB, 한 변 4096픽셀로 제한하고 백그라운드 스레드에서 처리합니다.

Paper Viewer의 실제 파일 선택·그림/수식·확대·폰트·입력·전력은 아직 확인 대기입니다. APK에는 실제 PDF·논문 본문·개인 대화·키가 없습니다.
