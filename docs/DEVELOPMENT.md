# Development setup and builds

English | [한국어](DEVELOPMENT.ko.md)

| Component | Selected configuration |
|---|---|
| Runtime | Android on the glasses |
| App language | Java 17 |
| Android SDK | minSdk 31 / compileSdk and targetSdk 36 |
| Build Tools | 36.0.0 |
| Gradle / AGP | 8.13 wrapper / 8.13.2 |
| C/NDK | Not introduced yet |

Install Java 17, Android SDK Platform 36 and Build Tools 36.0.0. Run from the repository root. The build does not require Node.js/npm or an approval-only vendor SDK.

```powershell
./scripts/build-native.ps1 -JavaHome 'C:/Tools/jdk17' -SdkRoot 'C:/Tools/AndroidSdk'
```

For repeated builds, place your paths in the Git-ignored `native/toolchain.local.json`:

```json
{
  "javaHome": "C:/Tools/jdk17",
  "sdkRoot": "C:/Tools/AndroidSdk"
}
```

Then run `./scripts/build-native.ps1`. The script changes environment variables only in its process and restores them afterward. It does not change global Java or account settings. It creates three APKs and checksums in ignored `dist/`.

With Python 3.10+, run `python scripts/check.py` to validate relative documentation links, JSON and XML. Android validation includes assembleDebug/lintDebug for all apps and Paper Viewer JVM unit tests.

Use the [ADB guide](ADB.md) for initial installation and connection, and [app usage](APPS.md) for features and device-test boundaries. Updating an installed APK requires the same signing key. Local debug and GitHub Actions debug keys can differ; do not mix them as updates. Uninstalling an app removes its private data.

## Documentation languages

`README.md`, `SECURITY.md` and `docs/*.md` are the English entry points. Their `.ko.md` siblings are complete Korean versions. Use the language link below each title. Keep progress, commands and limitations aligned when updating either language. Korean pages link to Korean guides; English pages link to English guides.

This change localizes repository documentation, not Android app strings. Current app controls remain Korean. `AGENTS.md` files are English contributor/agent instructions rather than duplicated user guides.

Official environment references: [AGP 8.13](https://developer.android.com/build/releases/agp-8-13-0-release-notes), [Platform Tools](https://developer.android.com/tools/releases/platform-tools), [NDK](https://developer.android.com/ndk/guides).
