# 검증 기록 — 2026-10-24

[English](VALIDATION.md) | 한국어

## 실기기 근거

- Hi Rokid 도구 상자로 Rokid ADB Helper를 안경에 설치하고 실행했습니다.
- Android 설정·기기 정보는 열렸지만 처음에는 개발자 옵션이 열리지 않았습니다. 빌드 번호를 7번 눌러 활성화한 후 진입했습니다.
- 무선 디버깅을 켜고 PC 페어링·인증 접속에 성공했습니다. device 상태를 확인한 뒤 Rokid RG-glasses, Android 12 / API 32를 읽었습니다.
- 수동 IP와 mDNS transport를 메모리에서 비교해 같은 안경임을 확인했습니다. 원문 식별자·접속 주소·코드는 저장소에 보관하지 않았습니다.
- Galaxy Watch7 / WearMouse Bluetooth 리모컨 연결을 확인했습니다. 모든 앱의 입력 검증이 끝났다는 뜻은 아닙니다.
- AnExplorer 설치와 파일 권한 설정을 완료했습니다. 앱에 Pro 7일 체험이 표시됐으며 종료 후 전송 범위는 미검증입니다.
- 사용자가 Paper Viewer에서 실제 PDF를 열었다고 보고했고, 문서와 3.2배 확대 상태가 보이는 실기기 화면을 제공했습니다. 렌더링 근거이며 읽기 편의·입력 매핑·복구 신뢰성을 모두 검증한 것은 아닙니다.
- PDF 화면에는 실제 논문과 개인 주변 환경이 있어 공개하지 않습니다.
- 사용자 제공 버전: 안경 1.27.009-20261014-150203, Hi Rokid G1.15.6.1012. 모든 펌웨어 호환성 근거는 아닙니다.

## 빌드 근거

세 앱 assembleDebug와 lintDebug, Paper Viewer JVM 테스트 4개 통과. APK 패키지·런처·min/target SDK·권한 0개·백업 제외·서명·zip 정렬을 확인했습니다. PDF·키 파일·자격 증명 패턴은 포함하지 않습니다.

새 저장소 빌드에서 Gradle task 179개를 실행했습니다. 앱별 lint 오류는 0개이며 GPT/Paper Viewer 각 경고 3개, Helper 2개입니다. 세로 화면 가정 및 Viewer 시제품의 문자열 리소스 미분리 경고입니다. Python 문서/JSON/XML 검사는 최초 20개 파일을 확인했고 이후 문서 추가는 APK를 변경하지 않습니다.

이전 ADB 읽기 스크립트는 지정 대상의 모델/API를 읽고, 두 transport가 있는데 대상을 생략하면 중단함을 확인했습니다. GitHub Actions는 구성했으며 로컬 검사와 CI 서버 결과는 구분합니다.

| APK | 바이트 | SHA-256 |
|---|---:|---|
| `gpt-viewer-android-debug.apk` | 19904 | `afdbb89ac661df271eccdf969db10953698a9f0fd750366cf1adc73d6c13c099` |
| `paper-viewer-android-debug.apk` | 51344 | `3a13889d6872e5b36f3632ec84e3d5ffd44d569cc70d0724da158cd3c40e5712` |
| `adb-helper-android-debug.apk` | 23732 | `884084ba34c3d5cc47113b4d867fe74219d2ff4b0cfbd8d824a89ee206d70a37` |

위 해시는 해당 빌드의 기록입니다. 이후 빌드의 값은 Git 제외 dist/artifacts.json에서 확인합니다.

## 저장소 구조 검증

앱 모듈을 `apps/`, 공통 UI를 `shared/android-ui/`로 나누고 Gradle wrapper·설정을 루트에 뒀습니다. 생성 파일은 `build/<module>/`을 사용합니다. Java/XML 원본 16개는 이전 구조와 바이트 단위로 같으며, 프로젝트 APK 세 개의 해시도 위 표와 같습니다.

루트에서 세 앱의 assembleDebug·lintDebug와 Paper Viewer JVM 테스트 4개가 통과했습니다. 현재 lint는 앱마다 오류 0개·경고 3개이며, 선택한 Gradle 버전·화면 방향 가정·시제품 문자열 관련 경고입니다. 이전 구조를 제거한 뒤 `./scripts/build.ps1 -App paper-viewer` 단독 빌드도 통과했습니다. 빌드 검사이며 안경 사용성을 다시 시험한 것은 아닙니다.

`dist/`는 하위 폴더 없이 APK와 `artifacts.json` 하나를 둡니다. 빌드에서 해시·패키지/SDK·권한·백업 제외·서명·정렬을 확인합니다. 기존 AnExplorer APK는 변경 없이 `external`로 표시하며, 외부 앱의 권한은 권한 0개인 프로젝트 앱과 구분합니다. `adb-info.ps1`은 제거했고 [ADB 가이드](ADB.ko.md)에 대상을 지정하는 표준 명령을 남겼습니다.

## 남은 검증

GPT Viewer 기기 표시·입력, PDF 선택기·파일 제공자·원본 직접 접근, 확대·이동·탐색·재실행, 폰트·긴 문서, 앱별 안경/워치/폰 조작, 통제된 전력·메모리·지연 측정이 남아 있습니다. 실제 API·폰 companion·카메라 AI·C/NDK 처리는 아직 없습니다.

현재 PDF 열기는 내부 사본을 한 부 만듭니다. 원본 읽기 전용 접근은 계획이며 완료된 수정이 아닙니다. 이 검증에서 개발 케이블 구매나 비용 발생 API 요청은 하지 않았습니다.
