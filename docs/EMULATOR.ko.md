# PC Android 개발 환경

[English](EMULATOR.md) | 한국어

Rokid Android Lab은 **PC 가상 개발 환경 전용**입니다. AOSP API 32 x86_64 VM에서 실제 APK를 실행하고 원본 에뮬레이터 화면을 패널 안에 붙입니다. 실제 안경·폰과 페어링·정보 조회·동기화·제어하지 않습니다. 완성 APK를 하드웨어에 설치하는 일은 별도 흐름입니다.

## 배치와 평소 사용법

```powershell
python tools/emulator.py
```

- **화면 위:** Start·Stop.
- **화면 아래:** 앱 선택·Build & run·Run APK·Send file·상시 표시 방향키/Enter/Back.
- **오른쪽:** Lab·App log 탭. 구분선을 드래그하면 로그 영역 크기를 조절합니다.
- **Lab:** 실행 과정 로그와 Check·Setup·Display 설정.
- **App log:** 선택 앱의 최근 로그, Refresh·Auto. 탭이 열려 있고 전용 VM 화면이 붙어 있으면 자동 갱신합니다. 최근 기록을 제한해서 보여주며 무한 보관 로그는 아닙니다. 종료·충돌 앱은 별도 디버거 확인이 필요할 수 있습니다.

화면 안에서 마우스·트랙패드로 포인터·클릭/더블클릭·상하좌우 스크롤을 사용하거나 아래 버튼을 사용합니다. Input mode 선택 줄은 없습니다. 버튼만 시험할 때는 방향키로 포커스를 옮긴 뒤 Enter를 누릅니다. Tab·Page 단축키는 CLI 개발 보조 기능일 뿐 앱의 필수 조작이 아닙니다.

Start 후 Android 부팅을 기다리고 앱을 선택해 Build & run을 누릅니다. 해당 앱의 빌드·lint 검사 후 설치·Activity 실행까지 합니다. Run APK는 빌드를 생략합니다. Setup·Check는 Lab 탭의 최초 준비·진단 기능이며 평소 매번 누를 필요는 없습니다.

추가 Python 패키지 없이 Windows API로 원본 창을 붙입니다. SDK 시작 때 잠깐 독립 창이 보일 수 있고 크기를 바꿔도 화면 비율을 유지합니다. headless로 시작한 VM은 Stop 후 패널에서 Start해야 원본 화면이 생깁니다.

Stop은 전용 VM만 종료합니다. 패널을 닫으면 진행 중 작업을 마친 뒤 붙어 있는 VM도 종료하며 앱·파일은 남습니다. SDK 종료에 실패하면 패널 파괴 전 원본 창을 분리합니다. wipe·앱 자동 삭제·데이터 초기화는 하지 않습니다.

## 로컬 화면 설정

초기값은 **임시 480 × 640·160 dpi·글꼴 배율 1.0**이며 안경에서 읽은 실측값이 아닙니다.

VM을 Stop하고 **Lab → Display…**에서 폭·높이·밀도·글꼴 배율을 입력한 뒤 Apply locally를 누릅니다. 다시 Start하면 적용됩니다. API는 32를 유지합니다. 값은 Git 제외 `.emulator/display.local.json`에만 저장합니다. 이전 버전의 로컬 숫자 설정은 수동 설정으로 보존하며 이를 위해 실제 기기에 접속하지 않습니다.

실기기 조회 버튼·CLI capture 명령·기기/IP 입력은 없습니다. SDK 소유 가상 transport만 제어합니다. 내부적으로 루프백 전용 ADB 서버 5039와 VM 콘솔 5586을 사용합니다. 무선 자동 연결은 끄고 USB 필터로 일반 실기기 연결을 제외합니다. connect/pair 명령이나 기존 PC ADB 서버 재시작은 사용하지 않습니다. 이 포트는 PC 내부 설정이지 안경 주소가 아닙니다.

Rokid 펌웨어·서비스, 광학, 실제 Bluetooth 주변기기, 카메라/NPU 드라이버, 실제 배터리는 재현하지 않습니다. PC VM 지연·메모리·전력은 하드웨어 측정값이 아닙니다. 이후 NDK 모듈은 VM용 x86_64 빌드와 Lab 밖의 실제 기기 ABI 빌드가 각각 필요합니다. 실제 기기 연동은 Lab 밖에 두고 여기서는 모의 데이터를 사용합니다.

## Send file

일반 파일을 원래 파일명으로 Android `/sdcard/Download/`에 넣습니다. 이름이 있으면 숫자를 붙이며 자동으로 열거나 설치하지 않습니다. 파일 관리자 또는 앱 파일 선택기의 내부 저장소 → Download에서 엽니다. Paper Viewer에서는 PDF 열기를 사용합니다.

전송 자체에 PDF 전용 제한은 없습니다. 받는 앱의 형식·크기 제한은 그대로이며 Paper Viewer는 여전히 최대 200 MiB PDF만 읽습니다. 기존 앱 폴더 PDF는 이동·삭제하지 않습니다. VM으로만 전송하며 파일을 공개하거나 실제 안경으로 보내지 않습니다.

VM 디스크·문서·화면 설정·로그·스크린샷은 Git 제외 `.emulator/`의 개인 자료입니다. 이 폴더를 공개하지 않습니다. APK 서명 키가 다르면 오류를 보여주며 데이터가 없어지는 앱 삭제를 자동으로 하지 않습니다.

## 터미널과 검사

Windows, Tk가 포함된 Python 3.10 이상, Java 17과 [개발 환경](DEVELOPMENT.ko.md)의 SDK 설정을 사용합니다. 기존 Git 제외 `toolchain.local.json`에서 본인 경로를 읽습니다. 새 저장소 폴더·Python 외부 패키지·계정·제조사 SDK는 필요하지 않습니다.

```powershell
python tools/emulator.py doctor
python tools/emulator.py setup
python tools/emulator.py display --width 480 --height 640 --density 160
python tools/emulator.py start
python tools/emulator.py run paper-viewer --build
python tools/emulator.py file "C:/MyFiles/example.txt"
python tools/emulator.py logs paper-viewer
python tools/emulator.py stop
```

터미널 전용 start는 SDK 독립 실행용이며 통합 화면은 기본 GUI로 엽니다. `start --headless`는 자동 가상 검증용입니다. 기기 명령은 실기기 transport를 거부하고 온라인 qemu와 전용 AVD 이름을 확인합니다. `python -m unittest discover -s tests -v`, `python scripts/check.py`로 검사합니다. 로컬 근거는 [검증 기록](VALIDATION.ko.md)을 참고합니다. 현재는 로컬 검토 작업이며 push를 뜻하지 않습니다.

공식 참고: [Android Emulator](https://developer.android.com/studio/run/emulator-commandline), [ADB 명령 옵션](https://android.googlesource.com/platform/packages/modules/adb/+/refs/heads/main/docs/user/adb.1.md), [무선 자동 연결 설정](https://android.googlesource.com/platform/packages/modules/adb/+/refs/heads/android16-s2-release/adb_mdns.cpp), [Windows 원본 창 부착](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setparent).
