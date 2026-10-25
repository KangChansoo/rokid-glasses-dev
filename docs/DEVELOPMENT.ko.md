# 개발 환경과 빌드

[English](DEVELOPMENT.md) | 한국어

| 구성 | 현재 선택 |
|---|---|
| 실행 위치 | 안경의 Android |
| 언어 | Java 17 |
| Android | minSdk 31 / compileSdk·targetSdk 36 |
| Build Tools | 36.0.0 |
| Gradle / AGP | 8.13 wrapper / 8.13.2 |
| C/NDK | 아직 미도입 |

Java 17과 Android SDK Platform 36 / Build Tools 36.0.0을 설치하고 저장소 루트에서 실행합니다. Node.js/npm이나 승인 SDK는 필요하지 않습니다.

```powershell
./scripts/build.ps1 -JavaHome 'C:/Tools/jdk17' -SdkRoot 'C:/Tools/AndroidSdk'
```

반복 실행은 Git 제외 파일 `toolchain.local.json`에 본인 경로를 넣어 사용할 수 있습니다.

```json
{
  "javaHome": "C:/Tools/jdk17",
  "sdkRoot": "C:/Tools/AndroidSdk"
}
```

설정 후 `./scripts/build.ps1`만 실행합니다. 스크립트는 현재 프로세스에서만 환경 변수를 적용하고 되돌립니다. 다른 프로젝트의 전역 Java/계정 설정을 바꾸지 않습니다. APK는 Git 제외 `dist/`에 생성되며 메타데이터는 `artifacts.json` 하나로 갱신합니다.

Python 3.10 이상에서 `python scripts/check.py`로 문서 상대 링크, JSON, XML을 검사합니다. Android 빌드는 세 앱 assembleDebug/lintDebug와 Paper Viewer의 JVM 단위 테스트를 포함합니다.

첫 설치와 연결은 [ADB 가이드](ADB.ko.md), 앱 기능과 실기기 대기 항목은 [앱 설명](APPS.ko.md)을 참고합니다. APK 업데이트는 기존 설치본과 같은 서명 키가 필요합니다. 로컬 debug 키와 GitHub Actions debug 키는 다를 수 있으므로 혼용하지 않습니다. 앱 삭제 시 앱 내부 데이터도 삭제됩니다.

공식 환경: [AGP 8.13](https://developer.android.com/build/releases/agp-8-13-0-release-notes), [Platform Tools](https://developer.android.com/tools/releases/platform-tools), [NDK](https://developer.android.com/ndk/guides).



## 브랜치 운영

| 브랜치 | 용도 |
|---|---|
| `main` | 릴리즈용. 릴리즈 승인 후 검증된 `dev` 변경을 받습니다. |
| `dev` | 완료한 개발 작업을 통합합니다. |
| `feature/<name>` | `dev`에서 시작하는 앱·기능·수정·문서 작업 단위입니다. |

이름은 `feature/paper-viewer`, `feature/gpt-viewer`, `feature/paper-viewer-navigation`처럼 짓습니다. 앱 코드는 `apps/` 아래 폴더로 관리하고, 브랜치는 변경 작업을 위한 임시 공간으로 사용합니다.

새 작업은 최신 개발 브랜치에서 시작합니다.

```powershell
git switch dev
git pull --ff-only origin dev
git switch -c feature/paper-viewer-navigation
```

feature 브랜치에서 커밋하고 필요한 검사를 실행합니다. 앱 변경은 `./scripts/build.ps1`, 문서 변경은 `python scripts/check.py`를 사용합니다. 동작을 바꿨다면 로컬 빌드 외에 해당 실기기 검증도 필요합니다. 브랜치를 공유하거나 PR을 만들 때 feature 브랜치를 push하고 대상은 `dev`로 설정합니다.

검사를 통과한 작업을 통합합니다.

```powershell
git switch dev
git pull --ff-only origin dev
git merge --no-ff feature/paper-viewer-navigation
git push origin dev
```

다음 작업도 `dev`에서 새 feature 브랜치를 만들어 진행합니다. 릴리즈할 때는 통합 빌드와 필요한 실기기 동작을 확인한 뒤 `dev`를 `main`으로 merge하고 `main`을 push합니다. 릴리즈 반영은 별도 결정이며 매 기능 통합 때 자동으로 하지 않습니다. 개발 작업을 `main`에 직접 커밋하거나 공유 이력을 force-push하지 않습니다. 작업 통합 후 로컬 체크아웃은 `dev`에 둡니다.

## 앱별 구조

독립 앱은 `apps/adb-helper`, `apps/gpt-viewer`, `apps/paper-viewer`에 나뉘고 공통 UI는 `shared/android-ui` 라이브러리에 둡니다. Gradle 설정·wrapper·개인 toolchain.local.json은 저장소 루트에 있습니다. 루트를 Android/Gradle 프로젝트로 엽니다.

생성 결과는 `build/<module>/`에 모아 앱 폴더에는 원본과 모듈 설정만 남깁니다. src/main/java, src/main/res, src/test는 Android의 표준 모듈 구조입니다.

```powershell
# 앱 하나 빌드·lint. Paper Viewer는 단위 테스트도 실행합니다.
./scripts/build.ps1 -App paper-viewer
# 세 앱 전체 빌드·검사.
./scripts/build.ps1
```

dist는 하위 폴더 없이 프로젝트 APK와 선택적인 외부 APK, artifacts.json 하나를 둡니다. JSON은 파일명·출처 구분·패키지/버전·SDK·크기·SHA-256·권한·서명/정렬 검사 결과를 담습니다. 우리 APK는 기존 패키지 ID·권한 0개·백업 제외를 확인합니다. 외부 앱은 별도 권한을 가지며 external로 표시합니다. 서명 검사는 유효성을 확인하며 제공자 신원·신뢰를 보증하지는 않습니다.

AnExplorer APK는 선택 사항이고 빌드에서 다운로드하거나 Git에 넣지 않습니다. JSON은 dist에 실제 있는 APK를 반영합니다. 앱 하나를 빌드하면 해당 APK만 갱신하고 기존 파일들도 목록에 포함하며 다른 앱을 재빌드하지 않습니다.

## PC 에뮬레이터 개발

`python tools/emulator.py`로 독립된 API 32 환경을 구성·실행하고 안경 배포 전에 앱을 빌드·실행할 수 있습니다. 화면 값 읽기·디버깅·하드웨어 한계는 [Android 개발 환경](EMULATOR.ko.md)을 참고합니다.

## 문서 언어

`README.md`, `SECURITY.md`, `docs/*.md`는 영어 기본 문서이고 같은 이름의 `.ko.md`는 전체 한국어 버전입니다. 제목 아래 언어 링크로 이동합니다. 상태·명령·제약을 수정할 때 양쪽을 맞춥니다. 한국어 문서는 한국어 안내끼리, 영어 문서는 영어 안내끼리 연결합니다.

이번 작업은 저장소 문서 번역이며 Android 앱 문자열의 다국어화는 아닙니다. 현재 앱 조작 문구는 한국어입니다. `AGENTS.md`는 영문 기여·에이전트 지침으로 유지합니다.
