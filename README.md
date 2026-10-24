# Rokid Glasses Dev

화면이 있는 Rokid AI Glasses에서 직접 실행할 **Android 앱과 개발 도구**를 만듭니다. APK 설치부터 무선 ADB 연결까지 직접 확인한 경로에서 시작합니다.

## 처음 시작하기

1. [개발 환경](docs/DEVELOPMENT.md)을 준비하고 `./scripts/build-native.ps1`로 APK를 만듭니다.
2. `dist/adb-helper-android-debug.apk`를 폰으로 옮긴 뒤 **Hi Rokid → 홈 → 도구 상자 → 안경 앱 관리**에서 안경에 설치합니다.
3. Helper의 **기기 정보 → 빌드 번호 7번 → 개발자 옵션 → 무선 디버깅** 순서로 설정합니다.
4. [ADB 가이드](docs/ADB.md)에 따라 PC와 페어링하고 연결합니다. 기기 주소·포트·코드는 본인 화면의 값을 사용합니다.
5. GPT Viewer와 Paper Viewer는 [앱 설명](docs/APPS.md)에 따라 별도로 검증합니다.

**실기기 확인:** Helper 설치·Android 설정 열기·개발자 옵션 활성화·무선 ADB 인증 및 접속 성공. 연결 후 확인한 기기는 Rokid `RG-glasses`, Android 12 / API 32입니다. 두 Viewer의 실제 표시·입력·PDF 열기는 아직 검증 대기입니다.

## 구성

```text
native/
  adb-helper/            Android 설정을 여는 진단 APK
  gpt-viewer/            Hello World / 가상 답변 데모 APK
  paper-viewer/          안경 로컬 PDF 페이지 뷰어 APK
  common/                공통 녹색 화면과 Android 버튼
scripts/
  build-native.ps1       세 APK 빌드·검사·체크섬 생성
  adb-info.ps1           명시한 ADB 대상의 모델·버전 읽기
  check.py               문서 링크·JSON·XML 확인
docs/                    시작 방법·설계·검증·로드맵
measurements/            개인정보 없는 측정 양식
```

현재 앱은 Java로 작성했습니다. 필요한 처리 모듈에 **C/NDK/JNI**를 도입하고 Python은 PC 실험·분석·도구에 활용하는 방향입니다. 아직 C 코드·비전 처리·폰 companion은 없습니다.

GPT Viewer의 답변은 데모이며 실제 GPT 연결이 아닙니다. **ChatGPT 앱의 기존 대화와 OpenAI API 응답은 별도**입니다. 현재 앱은 기존 대화나 완료 이벤트를 읽지 않습니다.

소스는 이 저장소에서 관리하고 APK·PDF·개인 논문 본문·ADB 키·IP·기기 식별자·API 키는 커밋하지 않습니다. [보안 가이드](SECURITY.md)를 따릅니다. SDK/도구 배포본과 개인 서명 키도 포함하지 않습니다.

- [무선 ADB 시작과 두 줄 표시 설명](docs/ADB.md)
- [개발 환경·빌드](docs/DEVELOPMENT.md)
- [앱 사용법](docs/APPS.md)
- [전체 구조](docs/ARCHITECTURE.md)
- [검증 기록](docs/VALIDATION.md)
- [로드맵](docs/ROADMAP.md)
- [배터리 측정](docs/BATTERY.md)

Independent project; not affiliated with Rokid, OpenAI or WearMouse. Vendor software retains its own terms.
