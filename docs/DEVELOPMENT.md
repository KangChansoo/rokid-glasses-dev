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
./scripts/build.ps1 -JavaHome 'C:/Tools/jdk17' -SdkRoot 'C:/Tools/AndroidSdk'
```

For repeated builds, place your paths in the Git-ignored `toolchain.local.json`:

```json
{
  "javaHome": "C:/Tools/jdk17",
  "sdkRoot": "C:/Tools/AndroidSdk"
}
```

Then run `./scripts/build.ps1`. The script changes environment variables only in its process and restores them afterward. It does not change global Java or account settings. It creates APKs in ignored `dist/` and refreshes its single `artifacts.json` inventory.

With Python 3.10+, run `python scripts/check.py` to validate relative documentation links, JSON and XML. Android validation includes assembleDebug/lintDebug for all apps and Paper Viewer JVM unit tests.

Use the [ADB guide](ADB.md) for initial installation and connection, and [app usage](APPS.md) for features and device-test boundaries. Updating an installed APK requires the same signing key. Local debug and GitHub Actions debug keys can differ; do not mix them as updates. Uninstalling an app removes its private data.


## Branch workflow

| Branch | Purpose |
|---|---|
| `main` | Releases; receives tested changes from `dev` when a release is approved. |
| `dev` | Integration of completed development work. |
| `feature/<name>` | One app, feature, fix or documentation task, started from `dev`. |

Use names such as `feature/paper-viewer`, `feature/gpt-viewer` or `feature/paper-viewer-navigation`. Apps remain folders under `apps/`; branches are temporary workspaces for changes.

Start a task from the latest development branch:

```powershell
git switch dev
git pull --ff-only origin dev
git switch -c feature/paper-viewer-navigation
```

Commit on the feature branch and run the relevant checks. For app changes, use `./scripts/build.ps1`; for documentation, use `python scripts/check.py`. A local build does not replace device testing where behavior changed. Push the feature branch if sharing it or opening a pull request, and target `dev`.

After checks pass, integrate the completed task:

```powershell
git switch dev
git pull --ff-only origin dev
git merge --no-ff feature/paper-viewer-navigation
git push origin dev
```

Keep working through new feature branches from `dev`. For a release, check the integrated build and relevant device behavior, then merge `dev` into `main` and push `main`. Release promotion requires an explicit release decision; it is not part of every feature merge. Do not commit development work directly to `main` or force-push shared history. Leave the local checkout on `dev` after integration.

## App-oriented layout

Each independent app lives in `apps/adb-helper`, `apps/gpt-viewer` or `apps/paper-viewer`. Common UI is a library in `shared/android-ui`. Gradle settings, wrapper and private `toolchain.local.json` are at the repository root. Open that root as the Android/Gradle project.

Generated outputs are grouped under `build/<module>/` so the app folders contain source and module configuration only. The `src/main/java`, `src/main/res` and `src/test` hierarchy is Android's normal module layout.

```powershell
# Build and lint one app. Paper Viewer also runs its unit tests.
./scripts/build.ps1 -App paper-viewer
# Build and validate all three apps.
./scripts/build.ps1
```

`dist/` is flat: project APKs and any optional external APKs sit beside `artifacts.json`. The inventory includes filename, origin, package/version, SDK levels, size, SHA-256, permissions and signature/alignment checks. Project APKs must retain the expected package IDs, no permissions and backup exclusions. External apps have separate permissions and are marked `external`. Signature verification checks validity, not vendor identity or trust.

The external AnExplorer APK is optional, is not downloaded by the build, and is not committed. The inventory reflects existing APKs in dist. A single-app build updates that app and inventories the other files already present; it does not rebuild the other apps.

## PC emulator workflow

Use `python tools/emulator.py` to set up/start the isolated API 32 lab and build/run apps before device deployment. See the [local Android lab](EMULATOR.md) for display capture, debugging and hardware limits.

## Documentation languages

`README.md`, `SECURITY.md` and `docs/*.md` are the English entry points. Their `.ko.md` siblings are complete Korean versions. Use the language link below each title. Keep progress, commands and limitations aligned when updating either language. Korean pages link to Korean guides; English pages link to English guides.

This change localizes repository documentation, not Android app strings. Current app controls remain Korean. `AGENTS.md` files are English contributor/agent instructions rather than duplicated user guides.

Official environment references: [AGP 8.13](https://developer.android.com/build/releases/agp-8-13-0-release-notes), [Platform Tools](https://developer.android.com/tools/releases/platform-tools), [NDK](https://developer.android.com/ndk/guides).
