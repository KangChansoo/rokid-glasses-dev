"""Local Android API 32 lab. Standard library only; writes target our AVD only."""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import queue
import re
import shutil
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parent.parent
AVD = 'rokid_android32'
IMAGE = 'system-images;android-32;default;x86_64'
APPS = {name: f'dev.rokidapps.{package}' for name, package in (
    ('paper-viewer', 'paperviewer'), ('gpt-viewer', 'gptviewer'), ('adb-helper', 'adbhelper'))}
KEYS = {'back': '4', 'enter': '66', 'tab': '61', 'up': '19', 'down': '20',
        'left': '21', 'right': '22', 'page-up': '92', 'page-down': '93'}
DEFAULT = dict(api=32, width=480, height=640, density=160, fontScale=1.0, source='provisional')


def display_profile(size: str, density: str, api: str, font: str) -> dict:
    """Prefer current wm overrides to physical values. Store no raw device identity."""
    sizes = re.search(r'Override size:\s*(\d+)x(\d+)', size) or re.search(r'Physical size:\s*(\d+)x(\d+)', size)
    densities = re.search(r'Override density:\s*(\d+)', density) or re.search(r'Physical density:\s*(\d+)', density)
    if not sizes or not densities:
        raise ValueError('Could not read Android display size/density.')
    width, height = map(int, sizes.groups())
    return validate_profile(dict(api=int(api.strip()), width=width, height=height,
                                 density=int(densities[1]), fontScale=1.0 if font.strip() == 'null' else float(font.strip()), source='device-display'))


def validate_profile(profile: dict) -> dict:
    if profile['api'] != 32:
        raise ValueError('This lab uses API 32. A different device API needs a separate system image/profile.')
    for key, low, high in (('width', 240, 4096), ('height', 240, 4096), ('density', 72, 640)):
        value = profile[key]
        if type(value) is not int or not low <= value <= high:
            raise ValueError(f'Invalid display {key}.')
    font = profile['fontScale']
    if not isinstance(font, (float, int)) or not math.isfinite(font) or not 0.5 <= font <= 3:
        raise ValueError('Invalid font scale.')
    if profile['source'] not in ('provisional', 'device-display'):
        raise ValueError('Invalid profile source.')
    return {key: profile[key] for key in DEFAULT}


def online_emulators(devices: str) -> list[str]:
    return [fields[0] for line in devices.splitlines() if len(fields := line.split()) >= 2
            and re.fullmatch(r'emulator-\d+', fields[0]) and fields[1] == 'device']


class Lab:
    def __init__(self, root: Path = ROOT):
        self.root = root
        self.state = root / '.emulator'
        self.profile_path = self.state / 'display.local.json'
        local = root / 'toolchain.local.json'
        config = json.loads(local.read_text(encoding='utf-8-sig')) if local.exists() else {}
        sdk = config.get('sdkRoot') or os.environ.get('ANDROID_HOME')
        if not sdk:
            raise RuntimeError('Configure sdkRoot in toolchain.local.json or set ANDROID_HOME. See docs/EMULATOR.md.')
        self.sdk = Path(sdk)
        self.env = os.environ.copy()
        self.env.update(ANDROID_HOME=str(self.sdk), ANDROID_AVD_HOME=str(self.state / 'avd'),
                        ANDROID_EMULATOR_HOME=str(self.state))
        java = config.get('javaHome') or os.environ.get('JAVA_HOME')
        if java:
            self.env['JAVA_HOME'] = java
        self.adb = self.sdk / 'platform-tools/adb.exe'
        self.emulator = self.sdk / 'emulator/emulator.exe'
        self.commands = self.sdk / 'cmdline-tools/latest/bin'

    def execute(self, args, timeout=60, input=None) -> str:
        result = subprocess.run([str(arg) for arg in args], cwd=self.root, env=self.env, input=input,
                                capture_output=True, text=True, encoding='utf-8', errors='replace',
                                timeout=timeout, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        if result.returncode:
            self.state.mkdir(exist_ok=True)
            (self.state / 'command-error.log').write_text(result.stderr + '\n' + result.stdout, encoding='utf-8')
            detail = result.stderr.strip()[:3000] + '\n' + result.stdout.strip()[-2000:]
            raise RuntimeError(detail.strip() + '\nFull output: .emulator/command-error.log')
        return result.stdout.strip()

    def adb_read(self, serial, *args) -> str:
        return self.execute([self.adb, '-s', serial, *args])

    def profile(self) -> dict:
        return validate_profile(json.loads(self.profile_path.read_text(encoding='utf-8')) if self.profile_path.exists() else DEFAULT.copy())

    def describe(self) -> str:
        p = self.profile()
        return f"API {p['api']} | {p['width']} x {p['height']} | {p['density']} dpi | font {p['fontScale']} | {p['source']}"

    def capture(self, serial: str) -> str:
        if self.adb_read(serial, 'get-state') != 'device':
            raise RuntimeError('The explicit capture device must be online and authorized.')
        p = display_profile(self.adb_read(serial, 'shell', 'wm', 'size'),
                            self.adb_read(serial, 'shell', 'wm', 'density'),
                            self.adb_read(serial, 'shell', 'getprop', 'ro.build.version.sdk'),
                            self.adb_read(serial, 'shell', 'settings', 'get', 'system', 'font_scale'))
        self.state.mkdir(exist_ok=True)
        self.profile_path.write_text(json.dumps(p, indent=2) + '\n', encoding='utf-8')
        return 'Read-only display capture saved locally. Restart the lab emulator to apply.\n' + self.describe()

    def target(self, required=True) -> str | None:
        matches = []
        for serial in online_emulators(self.execute([self.adb, 'devices'])):
            try:
                virtual = self.adb_read(serial, 'shell', 'getprop', 'ro.kernel.qemu') == '1'
                name = self.adb_read(serial, 'emu', 'avd', 'name').splitlines()[0]
                if virtual and name == AVD:
                    matches.append(serial)
            except (RuntimeError, IndexError, subprocess.TimeoutExpired):
                continue
        if len(matches) > 1:
            raise RuntimeError('Multiple lab emulator instances found. Close the extra instance.')
        if not matches and required:
            raise RuntimeError('Start the lab emulator first. Physical glasses and other AVDs are never selected.')
        return matches[0] if matches else None

    def setup(self) -> str:
        if self.target(required=False):
            raise RuntimeError('Stop the lab emulator before configuring it.')
        self.state.mkdir(exist_ok=True)
        (self.state / 'avd').mkdir(exist_ok=True)
        image = self.sdk / 'system-images/android-32/default/x86_64/system.img'
        if not self.emulator.exists() or not image.exists():
            self.execute([self.commands / 'sdkmanager.bat', f'--sdk_root={self.sdk}', 'emulator', IMAGE],
                         timeout=2400, input='n\n')
        avd_dir = self.state / 'avd' / f'{AVD}.avd'
        if not (avd_dir / 'config.ini').exists():
            self.execute([self.commands / 'avdmanager.bat', 'create', 'avd', '-n', AVD, '-k', IMAGE,
                          '-p', avd_dir], timeout=180, input='no\n')
        config_path = avd_dir / 'config.ini'
        config = dict(line.split('=', 1) for line in config_path.read_text(encoding='utf-8').splitlines() if '=' in line)
        p = self.profile()
        config.update({'avd.ini.displayname': 'Rokid Android Lab',
                       'hw.lcd.width': str(p['width']), 'hw.lcd.height': str(p['height']),
                       'hw.lcd.density': str(p['density']), 'hw.ramSize': '2048', 'hw.cpu.ncore': '2',
                       'hw.keyboard': 'yes', 'hw.dPad': 'yes', 'hw.mainKeys': 'yes',
                       'hw.initialOrientation': 'portrait' if p['height'] >= p['width'] else 'landscape',
                       'hw.camera.back': 'none', 'hw.camera.front': 'none', 'hw.audioInput': 'no',
                       'hw.gpu.enabled': 'yes', 'hw.gpu.mode': 'auto', 'disk.dataPartition.size': '2G',
                       'skin.name': f"{p['width']}x{p['height']}", 'skin.path': f"{p['width']}x{p['height']}",
                       'showDeviceFrame': 'no', 'fastboot.forceColdBoot': 'yes'})
        config_path.write_text(''.join(f'{key}={value}\n' for key, value in config.items()), encoding='utf-8')
        return 'Lab AVD configured.\n' + self.describe()

    def doctor(self) -> str:
        if not self.emulator.exists():
            return 'Emulator not installed. Run setup first.\n' + self.describe()
        return self.describe() + '\n' + self.execute([self.emulator, '-accel-check'])

    def start(self, headless=False) -> str:
        serial = self.target(required=False)
        process = None
        if not serial:
            self.setup()
            self.execute([self.emulator, '-accel-check'])
            args = [str(self.emulator), '-avd', AVD, '-no-snapshot', '-no-audio', '-no-boot-anim',
                    '-camera-back', 'none', '-camera-front', 'none']
            if headless:
                args.append('-no-window')
            with (self.state / 'emulator.log').open('ab') as log:
                process = subprocess.Popen(args, cwd=self.root, env=self.env, stdout=log, stderr=log,
                                           creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        deadline = time.monotonic() + 240
        while time.monotonic() < deadline:
            if process and process.poll() is not None:
                raise RuntimeError('Emulator exited. Check ignored .emulator/emulator.log.')
            serial = self.target(required=False)
            if serial and self.adb_read(serial, 'shell', 'getprop', 'sys.boot_completed') == '1':
                observed = display_profile(self.adb_read(serial, 'shell', 'wm', 'size'),
                                           self.adb_read(serial, 'shell', 'wm', 'density'),
                                           self.adb_read(serial, 'shell', 'getprop', 'ro.build.version.sdk'), '1.0')
                if any(observed[key] != self.profile()[key] for key in ('api', 'width', 'height', 'density')):
                    raise RuntimeError('Emulator display does not match the saved profile. Stop and start it to reconfigure.')
                self.adb_read(serial, 'shell', 'settings', 'put', 'system', 'font_scale', str(self.profile()['fontScale']))
                return 'Lab emulator ready.\n' + self.describe()
            time.sleep(2)
        raise RuntimeError('Emulator boot timed out; inspect .emulator/emulator.log. The VM was left running.')

    def launch(self, app: str, build=False) -> str:
        serial = self.target()
        if build:
            command = [shutil.which('pwsh') or 'powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                       self.root / 'scripts/build.ps1', '-App', app]
            self.execute(command, timeout=1200)
        serial = self.target()  # Re-check ownership after a potentially long build.
        apk = self.root / 'dist' / f'{app}-android-debug.apk'
        if not apk.is_file():
            raise RuntimeError('APK missing. Use Build & run first.')
        self.adb_read(serial, 'install', '-r', str(apk))
        result = self.adb_read(serial, 'shell', 'am', 'start', '-W', '-n', APPS[app] + '/.MainActivity')
        if 'Status: ok' not in result:
            raise RuntimeError('Android did not report a successful Activity launch.\n' + result)
        return result

    def key(self, key: str) -> str:
        self.adb_read(self.target(), 'shell', 'input', 'keyevent', KEYS[key])
        return f'Sent Android {key}. This is not a measured Rokid temple gesture.'

    def send_pdf(self, path: Path) -> str:
        if not path.is_file() or path.suffix.lower() != '.pdf':
            raise ValueError('Choose an existing PDF file.')
        if path.stat().st_size > 200 * 1024 * 1024:
            raise ValueError('Paper Viewer accepts PDFs up to 200 MiB.')
        serial = self.target()
        # The project app folder offers a deterministic alternative to provider-specific pickers.
        folder = '/sdcard/Android/data/dev.rokidapps.paperviewer/files/Documents'
        self.adb_read(serial, 'shell', 'mkdir', '-p', folder)
        self.adb_read(serial, 'push', str(path.resolve()), folder + '/lab-document.pdf')
        return 'PDF sent to lab emulator only as lab-document.pdf (replaces the previous lab transfer).\nOpen Paper Viewer > 앱 폴더. It stays private in the ignored AVD data.'

    def logs(self, app: str) -> str:
        serial = self.target()
        pid = self.adb_read(serial, 'shell', 'pidof', '-s', APPS[app])
        if not re.fullmatch(r'\d+', pid):
            raise RuntimeError('App is not running; launch it first.')
        return self.adb_read(serial, 'logcat', '-d', '-t', '300', '--pid=' + pid) or 'No recent app logs.'

    def stop(self) -> str:
        return self.adb_read(self.target(), 'emu', 'kill')


def gui(lab: Lab):
    import tkinter as tk
    from tkinter import ttk, filedialog, simpledialog

    window = tk.Tk()
    window.title('Rokid Android Lab')
    window.geometry('790x650')
    window.minsize(690, 550)
    frame = ttk.Frame(window, padding=16)
    frame.pack(fill='both', expand=True)
    ttk.Label(frame, text='Rokid Android Lab', font=('Segoe UI', 19, 'bold')).pack(anchor='w')
    ttk.Label(frame, text='Real APKs on AOSP Android. Emulator screen opens in a separate window.').pack(anchor='w')
    profile = tk.StringVar(value=lab.describe())
    ttk.Label(frame, textvariable=profile).pack(anchor='w', pady=(6, 4))
    ttk.Label(frame, text='Provisional screen until captured. Rokid OS, temple/Bluetooth input and optics are not emulated.',
              wraplength=740).pack(anchor='w', pady=(0, 12))
    jobs = queue.Queue()
    controls = []
    busy = False
    status = tk.StringVar(value='Ready')
    output = tk.Text(frame, wrap='word', height=14)

    def submit(action):
        nonlocal busy
        if busy:
            return
        busy = True
        status.set('Working… setup/build/boot can take several minutes.')
        for control in controls:
            control.configure(state='disabled')
        def worker():
            try:
                jobs.put((True, action()))
            except Exception as error:
                jobs.put((False, str(error)))
        threading.Thread(target=worker, daemon=True).start()

    def button(parent, text, action):
        control = ttk.Button(parent, text=text, command=lambda: submit(action))
        control.pack(side='left', padx=(0, 5), pady=4)
        controls.append(control)

    def capture():
        serial = simpledialog.askstring('Read display profile', 'Exact first-column target from adb devices (read only):', parent=window)
        if serial:
            submit(lambda: lab.capture(serial.strip()))

    def pdf():
        path = filedialog.askopenfilename(parent=window, filetypes=[('PDF', '*.pdf')])
        if path:
            submit(lambda: lab.send_pdf(Path(path)))

    top = ttk.Frame(frame); top.pack(fill='x')
    button(top, 'Check environment', lab.doctor)
    button(top, 'Setup', lab.setup)
    button(top, 'Start emulator', lab.start)
    button(top, 'Stop emulator', lab.stop)
    capture_button = ttk.Button(top, text='Read glasses display', command=capture)
    capture_button.pack(side='left', pady=4); controls.append(capture_button)
    row = ttk.Frame(frame); row.pack(fill='x', pady=8)
    selected = tk.StringVar(value='paper-viewer')
    selector = ttk.Combobox(row, textvariable=selected, values=list(APPS), state='readonly', width=18)
    selector.pack(side='left', padx=(0, 8))
    def app_button(label, action):
        # Snapshot the selection on the Tk thread before starting background work.
        control = ttk.Button(row, text=label, command=lambda: submit(lambda app=selected.get(): action(app)))
        control.pack(side='left', padx=(0, 5), pady=4)
        controls.append(control)
    app_button('Build & run', lambda app: lab.launch(app, build=True))
    app_button('Run existing APK', lab.launch)
    app_button('App logs', lab.logs)
    transfer = ttk.Button(row, text='Send PDF', command=pdf)
    transfer.pack(side='left', pady=4); controls.append(transfer)
    ttk.Label(frame, text='Android input — use mouse/drag/scroll directly in the emulator window.').pack(anchor='w')
    for values in (('back', 'enter', 'tab', 'up', 'down'), ('left', 'right', 'page-up', 'page-down')):
        row = ttk.Frame(frame); row.pack(fill='x')
        for key in values:
            button(row, key.title(), lambda key=key: lab.key(key))
    ttk.Label(frame, textvariable=status).pack(anchor='w', pady=(10, 4))
    output.pack(fill='both', expand=True)
    output.insert('end', '1. Setup / Check environment\n2. Start emulator\n3. Select app > Build & run\n4. Test, inspect app logs, repeat.\n\nApp/AVD data and logs stay local under .emulator/.\n')

    def poll():
        nonlocal busy
        try:
            ok, message = jobs.get_nowait()
        except queue.Empty:
            pass
        else:
            status.set('Done' if ok else 'Needs attention')
            output.insert('end', ('\n' if ok else '\nERROR: ') + str(message) + '\n')
            output.see('end')
            profile.set(lab.describe())
            busy = False
            for control in controls:
                control.configure(state='normal')
        window.after(100, poll)
    window.after(100, poll)
    window.mainloop()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command')
    for name in ('gui', 'doctor', 'setup', 'stop'):
        commands.add_parser(name)
    start = commands.add_parser('start'); start.add_argument('--headless', action='store_true')
    capture = commands.add_parser('capture'); capture.add_argument('--serial', required=True)
    launch = commands.add_parser('run'); launch.add_argument('app', choices=APPS); launch.add_argument('--build', action='store_true')
    key = commands.add_parser('key'); key.add_argument('name', choices=KEYS)
    pdf = commands.add_parser('pdf'); pdf.add_argument('path', type=Path)
    logs = commands.add_parser('logs'); logs.add_argument('app', choices=APPS)
    args = parser.parse_args()
    lab = Lab()
    if not args.command or args.command == 'gui':
        gui(lab)
    elif args.command == 'capture':
        print(lab.capture(args.serial))
    elif args.command == 'start':
        print(lab.start(args.headless))
    elif args.command == 'run':
        print(lab.launch(args.app, args.build))
    elif args.command == 'key':
        print(lab.key(args.name))
    elif args.command == 'pdf':
        print(lab.send_pdf(args.path))
    elif args.command == 'logs':
        print(lab.logs(args.app))
    else:
        print(getattr(lab, args.command)())


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError, FileNotFoundError, subprocess.TimeoutExpired) as error:
        print(f'Error: {error}', file=sys.stderr)
        sys.exit(1)
