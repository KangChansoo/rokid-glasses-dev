# PC Android 개발 환경

[English](EMULATOR.md) | 한국어

PC에서 실제 APK를 개발·디버깅한 뒤 안경에서 하드웨어와 최종 사용성을 확인하기 위한 환경입니다. Python 패널로 독립된 Android Emulator AVD에서 우리 앱을 실행합니다. Rokid 펌웨어 이미지를 포함하지 않습니다.

## 안경과의 유사성

| 항목 | PC 환경 |
|---|---|
| Android API | 실기기에서 확인한 API 32에 맞춘 AOSP Android 12L x86_64 이미지입니다. |
| APK | 프로젝트의 같은 debug APK, 네이티브 Android UI와 PDF 렌더러를 사용합니다. |
| 화면 | 명시적으로 지정한 연결 기기에서 현재 픽셀 크기·화면 밀도·글꼴 배율을 읽어 맞출 수 있습니다. |
| 초기 화면 | **임시값 480 × 640, 160 dpi, 글꼴 배율 1.0입니다. 안경에서 실측한 값이 아닙니다.** |
| 마우스·키 | 에뮬레이터 마우스와 Android Back·Enter·Tab·방향키·Page Up/Down입니다. Rokid temple이나 Galaxy Watch의 검증된 입력 매핑이 아닙니다. |
| 하드웨어 | Rokid OS·서비스, 광학 화면, Bluetooth 기기 동작, 카메라/NPU 드라이버, 물리 배터리를 재현하지 않습니다. |
| 성능 | PC 에뮬레이터의 CPU·GPU·메모리·저장소는 다릅니다. 지연·메모리·전력 결과를 안경의 측정값으로 취급하지 않습니다. |

PC 편의를 위해 RAM 2 GB와 사용자 데이터 파티션 2 GB를 사용합니다. 안경에서 측정한 사양이 아닙니다. 이후 C/NDK 모듈은 이 VM용 x86_64 빌드와 안경 ABI에 맞는 빌드가 각각 필요합니다. PC 통과가 실제 하드웨어 호환성을 보장하지는 않습니다.

## 시작

Windows, Tk가 포함된 Python 3.10 이상, Java 17과 [개발 환경](DEVELOPMENT.ko.md)의 SDK 설정을 사용합니다. 기존 Git 제외 `toolchain.local.json`에서 Java/SDK 경로를 읽습니다. Python 외부 패키지·웹 서버·제조사 SDK·계정은 필요하지 않습니다.

```powershell
python tools/emulator.py
```

패널에서 다음 순서로 사용합니다.

1. **Setup**: 없는 공식 Emulator / API 32 AOSP x86_64 패키지를 설치하고 전용 AVD만 만듭니다. 다운로드는 몇 분 걸릴 수 있습니다. 미승인 SDK 라이선스는 공식 SDK 도구에서 직접 확인해야 하며 이 도구가 새 라이선스를 자동 승인하지 않습니다.
2. **Check environment**: VM 가속을 검사합니다. Windows에서는 필요하면 Windows Hypervisor Platform을 사용합니다. 기능 활성화에는 관리자와 재부팅이 필요할 수 있습니다. 도구가 Windows 기능을 변경하거나 재부팅하지 않습니다.
3. **Start emulator**: 별도 에뮬레이터 창을 열고 Android 부팅 완료와 화면 설정을 확인합니다.
4. 앱 선택 후 **Build & run**: 해당 앱의 기존 빌드·lint 검사를 실행하고 설치·Activity 실행까지 합니다. **Run existing APK**는 빌드를 생략합니다.
5. 에뮬레이터 창의 마우스, 패널의 Android 키 버튼, **App logs**를 사용합니다. Enter 전에 Tab·방향키로 버튼 포커스를 잡습니다. 로그는 선택한 실행 중 앱의 제한된 최근 기록이며 종료·충돌한 프로세스는 Android Studio Logcat이 필요할 수 있습니다.
6. **Stop emulator**: 전용 VM만 종료합니다. Python 패널만 닫으면 에뮬레이터는 계속 실행됩니다.

이전 APK와 서명 키가 달라 설치에 실패하면 키 차이를 직접 해결합니다. 도구가 앱을 자동 삭제하거나 데이터를 초기화하지 않습니다. Android Studio에서 저장소 루트를 열고 실행 중인 에뮬레이터를 대상으로 디버깅할 수도 있습니다.

## 안경 화면에 맞추기

[ADB 안내](ADB.ko.md)대로 무선 ADB를 다시 연결합니다. **Read glasses display**를 누르고 `adb devices` 첫 열의 정확한 대상을 입력합니다. 상태·API·화면 크기·밀도·글꼴 배율만 읽습니다. 허용한 화면 값만 로컬에 저장하며 IP·일련번호·페어링 코드·계정은 저장하지 않습니다.

읽은 뒤 VM을 Stop/Start하면 적용됩니다. VM이 이미 꺼져 있으면 Setup으로 설정한 뒤 Start할 수 있습니다. 다른 API를 읽으면 조용히 일치한다고 가정하지 않고 거부합니다. 화면 설정을 읽어도 제조사 글꼴·광학·입력 펌웨어·시스템 서비스는 재현하지 않습니다.

## PDF와 로컬 데이터

**Send PDF**는 직접 선택한 PDF를 에뮬레이터 Paper Viewer의 앱 폴더에 `lab-document.pdf`로 넣습니다. 같은 이름의 이전 파일을 대체합니다. Paper Viewer에서 **앱 폴더**를 눌러 선택합니다. 에뮬레이터 전용 전송이며 논문을 GitHub·서버·실제 안경으로 업로드하지 않습니다. Viewer가 내부 사본을 만드는 기존 동작은 그대로입니다.

AVD 설정·VM 디스크·테스트 PDF·읽은 화면 값·에뮬레이터 로그는 모두 Git 제외 `.emulator/`에 둡니다. 이 폴더와 스크린샷·로그를 공개하지 않습니다. 일반 재시작 시 VM 데이터는 유지됩니다. 도구가 wipe/reset 명령을 사용하지 않습니다. VM 데이터를 직접 지우면 설치 앱과 문서도 사라집니다.

## 터미널 명령

```powershell
python tools/emulator.py setup
python tools/emulator.py doctor
python tools/emulator.py start
python tools/emulator.py run paper-viewer --build
python tools/emulator.py key page-down
python tools/emulator.py logs paper-viewer
python tools/emulator.py stop
```

`capture --serial <target>`은 지정 기기를 읽고, `pdf <path>`는 선택 PDF를 전용 VM에 전송합니다. 자동 검증에는 `start --headless`를 사용할 수 있습니다. 설치·입력·파일 전송·종료는 온라인 emulator transport·가상 기기 속성·전용 AVD 이름을 확인한 뒤 실행합니다. 실제 안경과 다른 AVD를 쓰기 대상으로 선택하지 않습니다. 전역 ADB 서버를 재시작하지 않습니다.

PC 도구 검사는 `python -m unittest discover -s tests -v`, `python scripts/check.py`로 실행합니다. CI source job도 VM 다운로드·부팅 없이 검사합니다. 실제 부팅·렌더링 근거는 [검증 기록](VALIDATION.ko.md)에 별도로 남깁니다.

공식 참고: [Android Emulator](https://developer.android.com/studio/run/emulator-commandline), [AVD 설정](https://developer.android.com/studio/run/managing-avds), [하드웨어 가속](https://developer.android.com/studio/run/emulator-acceleration). 구현은 설치된 SDK의 emulator/avdmanager 도구를 사용하며 최신 공식 문서에는 이를 대체하는 새 Android CLI도 안내됩니다.
