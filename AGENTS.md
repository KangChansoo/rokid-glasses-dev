# Rokid Glasses Dev

Develop standalone Android APKs under apps/. Use Hi Rokid Toolbox for the first installation and authenticated wireless ADB for development. Keep existing apps independent. Follow apps/AGENTS.md.

- This is a fresh Android-focused workspace. Do not add agent-studio frameworks, approval-only SDKs, undocumented APIs or old experiments to the default path.
- Java is the minimal Android UI boundary. Prefer portable C via NDK/JNI for meaningful processing when requested; use Python for PC tooling and experiments. C processing is not implemented yet.
- Phone-side CXR-L is a future optional integration, not a dependency of the current APKs. Verify official contracts before implementation.
- Never commit real papers, extracted document text, conversations, account data, IP/MAC/serials, pairing codes, ADB keys, tokens, private logs, APKs or signing keys.
- Use an explicit adb -s target when more than one transport is present. A manual IP connection and an mDNS service can represent the same physical device. Never choose a write target merely by list order.
- Preserve native Android Back/mouse/Enter behavior. Do not silently add permissions or broad storage access.
- For source/docs run python scripts/check.py. For Android changes run scripts/build.ps1 (assemble/lint all apps and Paper Viewer unit tests); inspect final APK manifests and signatures.
- Record build checks and hardware observations separately. ADB Helper, wireless ADB and PDF page rendering have device evidence. GPT device display, complete input mappings, PDF usability/restoration and controlled performance measurements still need validation.

- User-facing documentation is English by default with complete .ko.md siblings and reciprocal language links. Update both versions together. App UI localization is separate.

- Apps are independent modules in apps/; shared Android UI is shared/android-ui/. The apps/AGENTS.md safety/resource rules also apply to that shared module. Gradle settings/wrapper are at the repository root; generated output is root build/.
- dist/ is a flat, Git-ignored APK folder. scripts/build.ps1 creates its single artifacts.json with hashes, package metadata and validation. Mark external APKs as external; do not bundle or re-sign them.
