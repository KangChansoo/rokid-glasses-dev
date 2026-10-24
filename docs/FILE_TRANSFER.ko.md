# PDF 전송과 파일 관리

[English](FILE_TRANSFER.md) | 한국어

AnExplorer는 **선택적인 타사 파일 관리자**이며 Paper Viewer의 구성 요소가 아닙니다. PDF 읽기에 Pro 라이선스는 필요하지 않습니다. 폰에서 안경으로 파일을 보내는 일과 Viewer가 내부 사본을 만드는 일은 구분합니다.

## 설치와 파일 권한

[제공자의 안경용 다운로드 페이지](https://anexplorer.io/download/glasses)를 사용합니다. 확인한 파일은 이 페이지가 연결한 AnExplorer 6.0.8 APK입니다. 이 저장소에서는 재배포하지 않습니다.

1. 단일 APK를 폰에 저장하고 **Hi Rokid → 홈 → 도구 상자 → 안경 앱 관리**로 **안경에 설치**합니다. ADB가 연결되어 있을 필요는 없습니다.
2. 안경에서 AnExplorer의 파일 접근 요청을 누르거나, Helper → Android 설정 → 앱 → 특별한 앱 액세스 → 모든 파일 액세스 → AnExplorer에서 파일 관리 권한을 켭니다. 메뉴 명칭은 다를 수 있습니다.
3. 이후 AnExplorer로 APK도 설치할 때만 ‘알 수 없는 앱 설치’를 별도로 허용합니다. PDF 파일 접근과 다른 설정입니다. 일반 공유 문서를 읽는 데 루트는 필요하지 않습니다.

모든 파일 권한은 AnExplorer에 부여하는 것이며 이 저장소의 APK에는 추가하지 않습니다. Android는 여전히 다른 앱의 Android/data 접근을 제한할 수 있습니다. 우선 일반 공유 문서를 사용하고 제한 우회를 전제로 하지 않습니다.

## 폰에서 안경으로

양쪽에 AnExplorer를 설치하고 같은 Wi-Fi에 연결합니다.

1. 안경: **홈 → Connect(연결) → Transfer(전송) → Receive(받기)**.
2. 폰: **Connect → Transfer → Send(보내기)**에서 PDF를 선택하고 받는 안경을 고릅니다.
3. 안경의 **Transfer → Received Files(받은 파일)**에서 확인합니다. 제공자는 기본 경로를 `/AnExplorer/Received/`로 안내하지만 실제 위치는 버전·설정에 따라 다를 수 있습니다.
4. PDF 길게 누르기 → **다른 앱으로 열기 → Paper Viewer APK**를 선택합니다. 일반 탭은 AnExplorer 자체 Viewer로 열릴 수 있습니다.

`Documents/Papers`는 선택적인 정리 폴더입니다. ‘다른 앱으로 열기’에 필수는 아닙니다. 앱 전용 폴더와 시스템 선택기는 [앱 설명](APPS.ko.md)을 참고합니다.

## 체험판과 유료 기능

설치 앱 화면에 **AnExplorer Pro 7일 체험**이 표시됐습니다. [공식 FAQ](https://anexplorer.io/questions)는 무료 기본 앱을 안내하지만, [요금표](https://anexplorer.io/pricing)는 Wi-Fi 공유와 Connect를 Pro 기능에 포함합니다. 종료 후 무료 전송의 정확한 동작은 **미검증**이며 공식 페이지의 기능 범위도 일관되지 않습니다. 체험 중 동작한다고 계속 무료라고 전제하지 않습니다.

체험 배너만으로 구독·자동결제 등록 여부를 알 수 없습니다. 실제 구매·구독 상태를 확인해야 합니다. 이 프로젝트는 결제를 시작하거나 라이선스를 관리하지 않습니다.

Paper Viewer는 AnExplorer Pro에 의존하지 않습니다. 현재 앱 내부 사본은 우리 앱이 독립적으로 렌더링하므로 기존 PDF 읽기는 별개입니다. 다른 파일 전송 수단으로 교체할 수 있습니다. 라이선스 우회 기능은 포함하지 않습니다.

## 대안: 대상을 지정한 ADB

인증된 ADB가 연결되어 있으면 PDF를 공유 저장소로 복사할 수 있습니다. 본인의 현재 주소와 파일 경로를 입력하며 저장소에 기록하지 않습니다.

```powershell
$deviceEndpoint = Read-Host '연결 IP:포트'
$pdfPath = Read-Host 'PC의 PDF 경로'
adb -s $deviceEndpoint shell getprop ro.product.model
adb -s $deviceEndpoint shell mkdir -p /sdcard/Documents/Papers
adb -s $deviceEndpoint push $pdfPath /sdcard/Documents/Papers/
```

쓰기 전 모델을 확인합니다. `adb push`는 이름이 같은 파일을 덮어쓸 수 있으므로 필요하면 목적지를 먼저 확인하거나 새 파일명을 사용합니다. 파일 관리자로 전송할 때 이 절차는 필수가 아닙니다. 고정 포트 대신 현재 주소와 [ADB 재연결 안내](ADB.ko.md)를 사용합니다.

실제 PDF·본문·논문이 보이는 화면을 GitHub나 클라우드에 올리지 않습니다. 공개 시각 예시는 직접 만든 가상 데모를 사용합니다.

근거: [제공자 전송 안내](https://anexplorer.io/transfer/android-to-android), [Android 모든 파일 접근](https://developer.android.com/training/data-storage/manage-all-files).
