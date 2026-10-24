# Public source and private device data

English | [한국어](SECURITY.ko.md)

Do not commit real PDFs, extracted text, conversations, account data, device serials, MAC/IP addresses, pairing codes, ADB keys, tokens, private logs/screenshots or signing keys. Git ignore rules do not remove tracked files or history; inspect the staged diff and tracked file list before publishing.

Current APKs declare no network, camera, microphone, account, location or all-files permissions. Helper opens public settings screens only and does not enable ADB itself. Paper Viewer keeps one private copy of the selected PDF without modifying the original. Backups are disabled and file/rendering sizes are bounded.

AnExplorer is external software with its own permissions, licensing and data practices. A storage permission granted to it does not grant the same permission to our apps. Its Pro trial is not a guarantee of free transfer after expiry. See [file transfer](docs/FILE_TRANSFER.md).

Pair ADB on a trusted PC/network with user approval. Enter codes at the terminal prompt; keep endpoints in local variables and do not publish connection data/logs. Specify an explicit -s target when multiple transports exist. After work, turn off Wireless debugging on the glasses; disconnecting the PC is not the same action.

There is no API connection yet. Future integration must not place OpenAI keys in APKs, BuildConfig/resources/assets, client code or GitHub. If a credential leaks, revoke/replace it at the provider first and address history separately.

Do not commit APKs or SDK/JDK/Gradle distributions. The verified official Gradle wrapper JAR is the development bootstrap exception. Keep debug/release signing keys in local tooling and use the same signing identity for updates.

Public visual examples must use synthetic documents. Do not publish the user's real-paper screenshots or surrounding personal/device information.
