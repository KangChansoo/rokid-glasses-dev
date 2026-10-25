# 앱과 설치

[English](APPS.md) | 한국어

| 앱 | 패키지 | 파일 |
|---|---|---|
| Rokid ADB Helper | dev.rokidapps.adbhelper | dist/adb-helper-android-debug.apk |
| GPT Viewer APK | dev.rokidapps.gptviewer | dist/gpt-viewer-android-debug.apk |
| Paper Viewer APK | dev.rokidapps.paperviewer | dist/paper-viewer-android-debug.apk |

Hi Rokid 도구 상자로 **안경에 설치**합니다. 연결된 안경을 명시한 ADB 설치도 가능합니다. 설치 후 실행 메뉴·터치패드 모드·버튼 모드·뒤로가기를 앱별로 확인합니다.

## 입력 기준

터치패드(포인터·클릭/더블클릭·두 손가락 상하좌우 스크롤)와 버튼(상하좌우·Enter·뒤로가기)을 별도 모드로 취급합니다. 각 모드만으로 필수 기능을 확인하며 PC 전용 Tab·Page 키로 대체하지 않습니다. 사용자가 확인한 기기 입력 범위이며 모든 앱의 검증 완료를 뜻하지는 않습니다. Paper Viewer는 현재 포인터 드래그·휠 이동을 구현했고 버튼 모드 전용 화면 이동은 남아 있습니다. 별도 더블클릭 명령은 구현하지 않았습니다.

## ADB Helper

실제 안경에서 설치·기기 정보·개발자 옵션·무선 디버깅 설정과 PC 페어링 성공을 확인했습니다. [전체 절차](ADB.ko.md)를 따릅니다.

## GPT Viewer

Hello World, 한글로 직접 작성한 가상 답변 3장, 다음·이전·처음·종료가 있습니다. 실제 OpenAI API나 기존 ChatGPT 대화는 연결되지 않습니다. 코드와 빌드는 준비됐으나 Viewer의 실기기 표시/입력 확인은 대기입니다.

## Paper Viewer

안경 내부의 PDF 원본 페이지를 Android PdfRenderer로 표시합니다. 그림·수식을 포함한 페이지 렌더링, 이전/다음, 확대, 포인터 드래그/휠을 구현했습니다. 한 문서만 보관하며 암호 PDF/OCR/검색/주석/여러 문서 책장은 지원하지 않습니다.

1. 먼저 `데모`를 실행합니다. 실제 논문 대신 기기에서 직접 만든 가상 PDF 3쪽입니다.
2. 본인 PDF를 안경으로 전송하고 `PDF 열기`의 시스템 파일 선택기로 선택합니다.
3. 선택기가 없으면 `앱 폴더` 버튼으로 앱 소유 Documents 위치를 확인합니다. 해당 위치로 업로드할 수 있는지는 별도 기기 확인이 필요합니다.
4. 파일 관리자에서 `다른 앱으로 열기 → Paper Viewer APK`를 지원하면 읽을 수 있는 content:// 문서를 전달할 수 있습니다. 이때 특정 원본 폴더는 필수가 아닙니다. [파일 전송](FILE_TRANSFER.ko.md)을 참고하세요.

앱 소유 폴더는 `/storage/emulated/0/Android/data/dev.rokidapps.paperviewer/files/Documents/`입니다. 선택기와 해당 폴더 접근이 모두 없다면 파일 입력 경로는 미해결이며 전체 저장소 권한으로 자동 우회하지 않습니다.

선택 PDF는 `files/current.pdf`로 내부 사본 한 부를 만들고 읽던 쪽을 기억합니다. 원본은 변경하지 않습니다. `문서 제거`는 내부 사본과 위치만 지웁니다. 백업은 비활성화합니다. 입력 200MB, 렌더링 최대 4백만 픽셀/약 16MB, 한 변 4096픽셀로 제한하고 백그라운드 스레드에서 처리합니다.

사용자 보고와 화면에서 **실제 PDF 페이지가 안경에 표시됨을 확인**했습니다. 읽기 UI·파일 처리는 시제품 단계입니다. 3.2배 확대 상태가 보였지만 확대·이동·입력 매핑·읽던 위치 복구의 신뢰성을 모두 검증한 것은 아닙니다. 폰트·긴 문서·전력도 확인이 필요합니다. APK에는 실제 PDF·논문 본문·개인 대화·키가 없습니다.


## 현재 복사 방식과 개선 계획

PDF를 선택하거나 외부에서 열면 현재는 내부 `files/current.pdf`로 복사하고 읽던 쪽을 초기화합니다. 앱 자체를 다시 열 때 내부 사본과 쪽을 복구합니다. 스트림 호환성과 접근 권한 수명 처리는 단순해지지만 중복 저장과 열기 지연이 발생합니다.

원본 읽기 전용 접근, 문서별 읽던 위치, 필요한 경우에만 제한된 임시 캐시를 쓰는 방식은 개선 계획이며 아직 구현하지 않았습니다. PdfRenderer에 직접 전달할 파일은 임의 위치를 읽을 수 있어야 합니다. 모든 ‘다른 앱으로 열기’ URI가 영구 권한을 제공한다고 가정하지 않습니다.

현재 앱의 조작 문구는 한국어입니다. 영문 저장소 문서가 영문 앱 UI 제공을 뜻하지 않습니다. 실제 논문과 개인 캡처는 저장소에 올리지 않습니다.

근거: [Android PdfRenderer](https://developer.android.com/reference/android/graphics/pdf/PdfRenderer), [문서 접근](https://developer.android.com/training/data-storage/shared/documents-files).
