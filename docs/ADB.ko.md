# 무선 ADB: 처음부터 연결하기

[English](ADB.md) | 한국어

ADB는 PC에서 안경의 앱을 설치·실행하고 파일을 전송하거나 로그를 확인하는 Android 개발 연결입니다. 안경에 직접 실행하는 APK로 설정 화면을 열어, 개발 케이블 없이 무선 연결한 경로를 기록합니다.

## 1. 첫 APK 설치

1. [개발 환경](DEVELOPMENT.ko.md)에서 빌드한 `dist/adb-helper-android-debug.apk`를 휴대폰으로 복사합니다.
2. Hi Rokid **홈 → 도구 상자 → 안경 앱 관리**에서 APK를 선택해 **안경에 설치**합니다. 폰 자체에 설치하면 폰 설정이 열리므로 설치 대상을 구분합니다.
3. 안경에서 **Rokid ADB Helper**를 실행합니다. Android 설정, 기기 정보, Wi-Fi, 개발자 옵션 화면을 여는 버튼이 있습니다.

## 2. 개발자 옵션 활성화: 이번 기기에서 확인한 핵심 단계

처음에는 개발자 옵션 버튼만 열리지 않았고 다른 설정 화면은 열렸습니다. 아래 순서로 활성화한 뒤 개발자 옵션에 들어갔습니다.

1. Helper → **기기 정보**를 엽니다.
2. **빌드 번호 / Build number**를 7번 눌러 개발자 활성화 메시지를 확인합니다.
3. Helper로 돌아와 **개발자 옵션**을 다시 엽니다.
4. **무선 디버깅 / Wireless debugging**을 켭니다. 스위치 옆 항목 이름을 누르면 상세 화면에 들어갈 수 있습니다.

Hi Rokid의 ‘안경 ADB 디버깅’과 Android 설정의 ‘무선 디버깅’은 구분합니다. IP를 알아냈거나 충전 케이블을 꽂았다는 사실만으로 ADB 접속이 열리지는 않습니다. 이 경로는 현재 사용 기기에서 확인했으며 모든 모델·펌웨어를 보장하지 않습니다.

## 3. PC 준비와 페어링

PC와 안경을 같은 공유기/LAN에 연결합니다. PC는 유선이어도 되지만 게스트 네트워크·클라이언트 격리는 검색·접속을 막을 수 있습니다. [공식 Platform Tools](https://developer.android.com/tools/releases/platform-tools)를 사용합니다.

```powershell
adb version
adb devices -l
adb mdns services
```

안경의 무선 디버깅 상세 화면에서 **페어링 코드로 기기 페어링**을 엽니다. 이 화면의 **IP·페어링 포트·6자리 코드**가 필요합니다. 화면을 열어 둔 채 아래처럼 입력합니다.

```powershell
$pairEndpoint = Read-Host '안경의 페어링 IP:포트'
adb pair $pairEndpoint
# 이어지는 프롬프트에 안경 화면의 코드를 직접 입력
```

`Successfully paired`는 인증 완료입니다. 코드를 명령줄 인자로 붙이거나 파일·Git·스크린샷에 저장하지 않습니다. 만료되면 화면을 다시 열어 새 코드와 포트를 사용합니다.

## 4. 연결과 확인

페어링이 끝나면 자동 연결될 수 있습니다. 자동 연결이 없으면 무선 디버깅 메인 화면 또는 `adb mdns services`의 **_adb-tls-connect._tcp**에 표시된 **연결 IP:포트**를 사용합니다. 페어링 서비스는 **_adb-tls-pairing._tcp**이며 용도가 다릅니다.

```powershell
$deviceEndpoint = Read-Host '안경의 연결 IP:포트'
adb connect $deviceEndpoint
adb devices -l
adb -s $deviceEndpoint shell getprop ro.product.model
adb -s $deviceEndpoint shell getprop ro.build.version.release
adb -s $deviceEndpoint shell getprop ro.build.version.sdk
```

페어링 포트와 연결 포트는 서로 다를 수 있습니다. 기본 포트 5555를 가정하지 않습니다. 네트워크·무선 디버깅 재시작 시 주소·포트가 바뀔 수 있습니다. `device` 상태와 기기 모델을 확인한 뒤 설치나 파일 쓰기를 진행합니다.

확인한 모델은 **Rokid RG-glasses, Android 12 / API 32**입니다. 실제 IP·MAC·일련번호·서비스 이름·페어링 코드는 이 문서에 기록하지 않습니다.

## 5. adb devices에 두 줄이 나오는 이유

수동 IP 접속과 mDNS 자동 접속이 같은 기기를 서로 다른 transport 이름으로 등록할 수 있습니다. 아래는 **실제 기기와 무관한 예시**입니다.

```text
192.0.2.10:35000                           device
adb-EXAMPLE._adb-tls-connect._tcp          device
```

이번 기기는 두 transport의 모델과 내부 일련번호를 메모리에서 비교해 **같은 물리적 안경**임을 확인했습니다. 식별값 원문은 저장하지 않았습니다. 일반적으로 두 줄이라는 이유만으로 언제나 같은 기기라고 판단하면 안 됩니다.

두 항목이 있으면 `adb shell` 등은 `more than one device/emulator`로 실패할 수 있습니다. **`-s`로 사용할 항목 하나를 지정**하면 됩니다. `-s`에는 `adb devices` 첫 열의 IP:포트 또는 mDNS 이름 전체를 그대로 넣습니다.

```powershell
# 두 transport가 있어도 대상을 명확히 지정
adb -s $deviceEndpoint shell getprop ro.product.model
adb -s $deviceEndpoint install -r ./dist/gpt-viewer-android-debug.apk
```

수동 연결만 정리하려면 `adb disconnect $deviceEndpoint`를 실행하고 목록을 다시 봅니다. mDNS 항목이 남아 있으면 그것을 `-s`로 사용할 수 있습니다. 자동 재연결 때문에 목록이 바뀔 수 있으므로 한 줄로 만드는 것보다 대상 지정이 확실합니다. 이 안내는 연결을 강제로 끊거나 PC의 전역 mDNS 설정을 바꾸지 않습니다.

## 6. 표준 명령으로 기기 정보 읽기

별도 정보 확인 스크립트 대신 대상을 지정한 표준 ADB 명령을 사용합니다.

```powershell
adb -s $deviceEndpoint shell getprop ro.product.model
adb -s $deviceEndpoint shell getprop ro.product.manufacturer
adb -s $deviceEndpoint shell getprop ro.build.version.release
adb -s $deviceEndpoint shell getprop ro.build.version.sdk
```

모델·버전만 읽으며 앱 설치·파일 전송·설정 변경은 하지 않습니다. 대상은 adb devices의 첫 열이며 하드웨어 일련번호일 필요는 없습니다.

## 7. 종료·다시 연결

작업 후 `adb disconnect $deviceEndpoint`로 PC 연결을 해제하고, 안경 설정의 무선 디버깅도 끕니다. disconnect만으로 기기 쪽 기능이 꺼지지는 않습니다. 다음 작업 때는 무선 디버깅을 켜고 현재 주소·포트를 확인합니다. PC 페어링이 유지되어 있으면 다시 코드를 입력할 필요가 없을 수 있습니다. 초기화·인증 해제·PC 키 변경 후에는 재페어링합니다. **연결이 끊겼다고 항상 페어링까지 지워지는 것은 아닙니다.** offline 또는 목록에서 사라진 것만으로 인증이 지워졌다고 판단하지 않습니다.

## Helper의 범위

Helper는 공개 Android Settings Intent만 요청합니다. ADB 자동 활성화, 설정 쓰기, 루트, 접근성 서비스, 숨겨진 API, 포트 개방 또는 코드 수집은 없습니다. 선언 권한 0개이며 모델/Android 버전만 화면에 표시합니다. 일반 앱이 읽는 ADB 설정값이 실제 상태를 반영하지 않을 수 있어 상태 추정 표시도 하지 않습니다.

다른 펌웨어에서 화면이 없거나 접근이 거부되면 그 결과를 표시합니다. 설정 화면의 존재·색상·터치 매핑은 펌웨어에 따라 다릅니다. 시스템이 차단한 경우 이 APK로 제한을 해제하지 않습니다.

## 공식 근거

- [Android 개발자 옵션 활성화](https://developer.android.com/studio/debug/dev-options#enable)
- [Android 무선 ADB와 대상 지정](https://developer.android.com/tools/adb)
- [Settings Intent](https://developer.android.com/reference/android/provider/Settings#ACTION_APPLICATION_DEVELOPMENT_SETTINGS)
- [ADB mDNS 구조](https://android.googlesource.com/platform/packages/modules/adb/+/HEAD/docs/dev/adb_wifi.md)
- [Rokid Toolbox](https://global.rokid.com/pages/faq)
