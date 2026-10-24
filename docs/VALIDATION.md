# 검증 기록 — 2026-10-24

## 실기기 확인

- Rokid ADB Helper APK를 Hi Rokid 도구 상자로 안경에 설치해 실행했습니다.
- Android 설정·기기 정보는 열렸으며 처음에는 개발자 옵션만 열리지 않았습니다.
- 기기 정보에서 빌드 번호를 7번 눌러 활성화한 후 개발자 옵션 진입에 성공했습니다.
- 무선 디버깅을 켜고 PC에서 페어링 및 ADB 연결 성공. 상태 `device` 확인 후 모델 Rokid `RG-glasses`, Android 12 / API 32를 읽었습니다.
- 수동 IP와 mDNS 이름 두 transport가 같은 기기임을 내부 식별값 비교로 확인했습니다. 원문 식별자·주소·코드는 저장하지 않았습니다.
- 사용자 제공 버전은 안경 `1.27.009-20261014-150203`, Hi Rokid `G1.15.6.1012`입니다. 모든 펌웨어 호환성을 보장하지 않습니다.

## 기존 코드의 확인 범위

세 앱 빌드와 lint, Paper Viewer JVM 테스트 4개, APK 패키지/권한 0개/백업 제외/서명/정렬을 확인한 Android 코드에서 시작합니다. 새 저장소에서도 동일 검사를 실행하고 결과를 아래에 기록합니다. 실제 PDF나 키 파일은 포함하지 않습니다.

두 Viewer의 실제 표시·입력·PDF 열기, 기본 터치/리모컨/WearMouse, 배터리는 아직 대기입니다. Helper와 ADB 성공을 Viewer 성공으로 확대 해석하지 않습니다. 설치 케이블 구매나 비용 발생 API 요청은 하지 않았습니다.

## 새 저장소에서 실행한 검사

- 세 앱 assembleDebug와 lintDebug, Paper Viewer JVM 단위 테스트 성공. 새 경로에서 179개 Gradle task를 실행했습니다.
- Python 문서/JSON/XML 검사 20개 통과. ADB 읽기 도구는 명시한 대상의 모델/API를 확인했고, 두 transport 상태에서 대상 생략 시 중단하는 것도 확인했습니다.
- APK 세 개의 런처·패키지·min/target SDK·권한 0개·백업 제외·서명·zip 정렬을 확인했습니다. PDF/키 파일과 자격 증명 패턴은 없습니다.
- GitHub Actions도 구성했지만 로컬 검사와 CI 서버 결과는 별도입니다.

| APK | 바이트 | SHA-256 |
|---|---:|---|
| `gpt-viewer-android-debug.apk` | 19904 | `afdbb89ac661df271eccdf969db10953698a9f0fd750366cf1adc73d6c13c099` |
| `paper-viewer-android-debug.apk` | 51344 | `3a13889d6872e5b36f3632ec84e3d5ffd44d569cc70d0724da158cd3c40e5712` |
| `adb-helper-android-debug.apk` | 23732 | `884084ba34c3d5cc47113b4d867fe74219d2ff4b0cfbd8d824a89ee206d70a37` |
