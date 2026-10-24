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
./scripts/build-native.ps1 -JavaHome 'C:/Tools/jdk17' -SdkRoot 'C:/Tools/AndroidSdk'
```

반복 실행은 Git 제외 파일 `native/toolchain.local.json`에 본인 경로를 넣어 사용할 수 있습니다.

```json
{
  "javaHome": "C:/Tools/jdk17",
  "sdkRoot": "C:/Tools/AndroidSdk"
}
```

설정 후 `./scripts/build-native.ps1`만 실행합니다. 스크립트는 현재 프로세스에서만 환경 변수를 적용하고 되돌립니다. 다른 프로젝트의 전역 Java/계정 설정을 바꾸지 않습니다. APK 세 개와 체크섬은 Git 제외 `dist/`에 생성됩니다.

Python 3.10 이상에서 `python scripts/check.py`로 문서 상대 링크, JSON, XML을 검사합니다. Android 빌드는 세 앱 assembleDebug/lintDebug와 Paper Viewer의 JVM 단위 테스트를 포함합니다.

첫 설치와 연결은 [ADB 가이드](ADB.ko.md), 앱 기능과 실기기 대기 항목은 [앱 설명](APPS.ko.md)을 참고합니다. APK 업데이트는 기존 설치본과 같은 서명 키가 필요합니다. 로컬 debug 키와 GitHub Actions debug 키는 다를 수 있으므로 혼용하지 않습니다. 앱 삭제 시 앱 내부 데이터도 삭제됩니다.

공식 환경: [AGP 8.13](https://developer.android.com/build/releases/agp-8-13-0-release-notes), [Platform Tools](https://developer.android.com/tools/releases/platform-tools), [NDK](https://developer.android.com/ndk/guides).


## 문서 언어

`README.md`, `SECURITY.md`, `docs/*.md`는 영어 기본 문서이고 같은 이름의 `.ko.md`는 전체 한국어 버전입니다. 제목 아래 언어 링크로 이동합니다. 상태·명령·제약을 수정할 때 양쪽을 맞춥니다. 한국어 문서는 한국어 안내끼리, 영어 문서는 영어 안내끼리 연결합니다.

이번 작업은 저장소 문서 번역이며 Android 앱 문자열의 다국어화는 아닙니다. 현재 앱 조작 문구는 한국어입니다. `AGENTS.md`는 영문 기여·에이전트 지침으로 유지합니다.
