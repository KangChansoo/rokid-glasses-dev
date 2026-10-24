# Rokid Glasses Dev

[English](README.md) | 한국어

**Rokid AI Glasses용 Android 앱을 직접 개발하며 임베디드 시스템과 AI를 탐구하는 개인 프로젝트**입니다.

직접 만든 PDF Viewer 시제품으로 실제 안경에서 PDF 페이지를 표시했습니다. 현재는 가독성·입력·파일 처리 방식을 개선하고, 이후 C/NDK 처리 모듈·스마트폰 연동·AI 기능으로 확장하려고 합니다.

## 진행 상황

- [x] Galaxy Watch를 리모컨으로 사용
- [x] 무선 ADB 개발 환경 구축
- [x] AnExplorer 파일 관리 환경 구성
- [ ] PDF Viewer 개발
- [ ] GPT Viewer 개발
- [ ] C/NDK 모듈 개발
- [ ] 스마트폰 연동
- [ ] 메모리·지연·전력 측정
- [ ] 카메라·AI 응용 탐구

Viewer 시제품은 있으며 미완료 표시는 지속적인 개발 과제를 뜻합니다. AnExplorer는 선택적인 타사 도구입니다. 설치한 앱에는 7일 Pro 체험이 표시되며, 체험 종료 후 무선 전송의 무료 사용 범위는 확인하지 못했습니다. [파일 전송 안내](docs/FILE_TRANSFER.ko.md)를 참고하세요.

## 현재 확인한 결과

| 구성 요소 | 현재 상태 |
|---|---|
| ADB Helper | 안경에 설치하고 Android 설정 열기 확인. 빌드 번호로 개발자 옵션 활성화. |
| 무선 ADB | Rokid RG-glasses / Android 12 / API 32에서 페어링·인증 접속·기기 정보 확인. |
| Galaxy Watch7 / WearMouse | Bluetooth 리모컨 입력 연결 확인. Viewer의 모든 조작과 호환되는지는 추가 검증 필요. |
| Paper Viewer | 실제 PDF 페이지가 안경에 표시됨을 확인. 읽기 UI·파일 처리는 시제품 단계. |
| GPT Viewer | 가상 답변 데모 빌드 준비. 실제 AI 연동과 기기 검증은 대기. |

현재 앱은 **Java와 Android 기본 API**를 사용합니다. C/NDK 처리, 카메라 AI, 폰 companion, 실제 API 연동은 아직 없습니다. GPT Viewer는 기존 ChatGPT 대화를 읽지 않습니다.

## 처음 시작하기

1. [개발 환경](docs/DEVELOPMENT.ko.md)을 준비하고 `./scripts/build-native.ps1`를 실행합니다.
2. `dist/adb-helper-android-debug.apk`를 폰으로 복사하고 **Hi Rokid → 홈 → 도구 상자 → 안경 앱 관리**에서 **안경에 설치**합니다. 메뉴 명칭은 앱 언어·버전에 따라 다를 수 있습니다.
3. Helper의 **기기 정보 → 빌드 번호 7번 → 개발자 옵션 → 무선 디버깅** 순서로 설정합니다.
4. [ADB 가이드](docs/ADB.ko.md)에 따라 현재 안경 화면의 페어링·연결 주소로 접속합니다.
5. [앱 설명](docs/APPS.ko.md)과 [PDF 전송](docs/FILE_TRANSFER.ko.md)에 따라 본인 문서를 시험합니다. 파일 관리자로 열 때 특정 폴더는 필수가 아닙니다.

## 저장소 구성

```text
native/
  adb-helper/            Android 설정을 여는 진단 도구
  gpt-viewer/            Hello World / 가상 답변 Viewer
  paper-viewer/          안경 로컬 PDF 페이지 Viewer
  common/                녹색 글자·검은 바탕의 공통 Android UI
scripts/
  build-native.ps1       빌드·lint·단위 테스트·APK 체크섬
  adb-info.ps1           명시한 ADB 대상의 모델·버전 읽기
  check.py               문서 링크·JSON·XML 검사
docs/                    영어·한국어 안내
measurements/            빈 배터리·입력 측정 양식
```

APK 산출물, 실제 논문·추출 본문·기기 식별자·개인 캡처·ADB 키·API 키·서명 키는 Git에 넣지 않습니다. APK에 PDF도 포함하지 않습니다. 현재 Viewer는 내부 사본 한 부를 만듭니다. 원본 직접 열기는 개선 계획이며 아직 구현하지 않았습니다. [보안 가이드](SECURITY.ko.md)를 참고하세요.

## 문서

- [무선 ADB](docs/ADB.ko.md)
- [파일 전송과 AnExplorer 제약](docs/FILE_TRANSFER.ko.md)
- [개발 환경·빌드](docs/DEVELOPMENT.ko.md)
- [앱과 현재 제약](docs/APPS.ko.md)
- [전체 구조](docs/ARCHITECTURE.ko.md)
- [검증 기록](docs/VALIDATION.ko.md)
- [로드맵](docs/ROADMAP.ko.md)
- [배터리 측정](docs/BATTERY.ko.md)

Rokid, OpenAI, WearMouse, AnExplorer와 제휴하지 않은 개인 프로젝트입니다. 타사 소프트웨어에는 각 제공자의 조건이 적용됩니다.
