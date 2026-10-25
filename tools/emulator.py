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
ADB_PORT = 5039
EMULATOR_PORT = 5586
NO_USB_DEVICE = 'rokid_android_lab_virtual_only'
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
                                 density=int(densities[1]), fontScale=1.0 if font.strip() == 'null' else float(font.strip()), source='manual'))


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
    if profile['source'] not in ('provisional', 'manual'):
        raise ValueError('Invalid profile source.')
    return {key: profile[key] for key in DEFAULT}


def online_emulators(devices: str) -> list[str]:
    return [fields[0] for line in devices.splitlines() if len(fields := line.split()) >= 2
            and re.fullmatch(r'emulator-\d+', fields[0]) and fields[1] == 'device']


def available_filename(name: str, existing: set[str]) -> str:
    if not name or name in ('.', '..') or any(char in name for char in ('/', '\\', '\r', '\n', '\0')):
        raise ValueError('Choose a file with a normal filename.')
    if len(name.encode('utf-8')) > 220:
        raise ValueError('Filename is too long for Android. Rename the file before sending.')
    original = Path(name)
    candidate = name
    number = 2
    while candidate in existing:
        candidate = f'{original.stem} ({number}){original.suffix}'
        number += 1
    return candidate


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
        self.env.pop('ANDROID_SERIAL', None)
        self.env.pop('ANDROID_ADB_SERVER_ADDRESS', None)
        self.env.update(ADB_SERVER_SOCKET=f'tcp:127.0.0.1:{ADB_PORT}',
                        ANDROID_ADB_SERVER_PORT=str(ADB_PORT), ADB_MDNS_AUTO_CONNECT='0')
        self._adb_lock = threading.Lock()
        self.env.update(ANDROID_HOME=str(self.sdk), ANDROID_AVD_HOME=str(self.state / 'avd'),
                        ANDROID_EMULATOR_HOME=str(self.state))
        java = config.get('javaHome') or os.environ.get('JAVA_HOME')
        if java:
            self.env['JAVA_HOME'] = java
        self.adb = self.sdk / 'platform-tools/adb.exe'
        self.emulator = self.sdk / 'emulator/emulator.exe'
        self.commands = self.sdk / 'cmdline-tools/latest/bin'

    def execute(self, args, timeout=60, input=None) -> str:
        command = [str(arg) for arg in args]
        if command[0] == str(self.adb):
            tail = command[1:]
            if tail != ['devices']:
                if (len(tail) < 3 or tail[0] != '-s' or not re.fullmatch(r'emulator-\d+', tail[1])
                        or tail[2] not in {'shell', 'emu', 'install', 'push', 'pull', 'logcat', 'exec-out'}):
                    raise ValueError('The Lab accepts emulator targets only; connect/pair/physical commands are unavailable.')
            with self._adb_lock:
                self._run([self.adb, '-P', str(ADB_PORT), '--one-device', NO_USB_DEVICE, 'start-server'])
            command = [str(self.adb), '-P', str(ADB_PORT), *tail]
        return self._run(command, timeout=timeout, input=input)

    def _run(self, args, timeout=60, input=None) -> str:
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
        if not re.fullmatch(r'emulator-\d+', serial):
            raise ValueError('Only a local emulator transport can be used by the Lab.')
        return self.execute([self.adb, '-s', serial, *args])

    def profile(self) -> dict:
        profile = json.loads(self.profile_path.read_text(encoding='utf-8')) if self.profile_path.exists() else DEFAULT.copy()
        # Preserve only old local dimensions; there is no device-capture operation anymore.
        if profile.get('source') == 'device-display':
            profile['source'] = 'manual'
        return validate_profile(profile)

    def describe(self) -> str:
        p = self.profile()
        return f"API {p['api']} | {p['width']} x {p['height']} | {p['density']} dpi | font {p['fontScale']} | {p['source']}"

    def configure_display(self, width: int, height: int, density: int, font_scale: float) -> str:
        profile = validate_profile(dict(api=32, width=width, height=height, density=density,
                                        fontScale=font_scale, source='manual'))
        if self.target(required=False):
            raise RuntimeError('Stop the virtual emulator before changing its display settings.')
        self.state.mkdir(exist_ok=True)
        self.profile_path.write_text(json.dumps(profile, indent=2) + '\n', encoding='utf-8')
        return 'Local display settings saved. Start the emulator to apply.\n' + self.describe()

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

    def start(self, headless=False, embedded=False) -> str:
        serial = self.target(required=False)
        process = None
        if not serial:
            self.setup()
            self.execute([self.emulator, '-accel-check'])
            args = [str(self.emulator), '-avd', AVD, '-port', str(EMULATOR_PORT), '-no-snapshot', '-no-audio', '-no-boot-anim',
                    '-camera-back', 'none', '-camera-front', 'none']
            if headless:
                args.append('-no-window')
            elif embedded:
                args.append('-no-skin')
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
        return f'Sent Android {key} to the lab emulator.'

    def send_file(self, path: Path) -> str:
        source = path.expanduser().resolve(strict=True)
        if not source.is_file():
            raise ValueError('Choose an existing file, not a folder.')
        # Validate before any device operation. Only the push protocol sees the filename;
        # it is never interpolated into an Android shell command.
        available_filename(source.name, set())
        serial = self.target()
        folder = '/sdcard/Download'
        self.adb_read(serial, 'shell', 'mkdir', '-p', folder)
        existing = set(self.adb_read(serial, 'shell', 'ls', '-1a', folder).splitlines())
        filename = available_filename(source.name, existing)
        destination = folder + '/' + filename
        self.execute([self.adb, '-s', serial, 'push', str(source), destination], timeout=600)
        return (f'Sent file to Download/{filename}.\n'
                'Open it using a file manager or the app file picker > internal storage > Download.\n'
                'The file was not opened or installed automatically.')

    def logs(self, app: str) -> str:
        serial = self.target()
        try:
            pid = self.adb_read(serial, 'shell', 'pidof', '-s', APPS[app])
        except RuntimeError as error:
            raise RuntimeError('The selected app is not running. Launch it to see its logs.') from error
        if not re.fullmatch(r'\d+', pid):
            raise RuntimeError('App is not running; launch it first.')
        return self.adb_read(serial, 'logcat', '-d', '-t', '300', '--pid=' + pid) or 'No recent app logs.'

    def stop(self) -> str:
        return self.adb_read(self.target(), 'emu', 'kill')


class NativeEmulatorHost:
    """Host the SDK-owned Qt window; Android rendering/input stays native."""
    def __init__(self, stage, lab):
        import ctypes
        from ctypes import wintypes as w
        if sys.platform != 'win32':
            raise RuntimeError('The integrated native display currently requires Windows.')
        self.ctypes, self.w, self.stage, self.lab = ctypes, w, stage, lab
        self.u = ctypes.WinDLL('user32', use_last_error=True)
        self.k = ctypes.WinDLL('kernel32', use_last_error=True)
        self.callback = ctypes.WINFUNCTYPE(w.BOOL, w.HWND, w.LPARAM)
        self.u.EnumWindows.argtypes = (self.callback, w.LPARAM)
        self.u.GetWindowTextW.argtypes = (w.HWND, w.LPWSTR, ctypes.c_int)
        self.u.GetWindowThreadProcessId.argtypes = (w.HWND, ctypes.POINTER(w.DWORD))
        self.u.GetWindowLongPtrW.argtypes = (w.HWND, ctypes.c_int)
        self.u.GetWindowLongPtrW.restype = ctypes.c_ssize_t
        self.u.SetWindowLongPtrW.argtypes = (w.HWND, ctypes.c_int, ctypes.c_ssize_t)
        self.u.SetWindowLongPtrW.restype = ctypes.c_ssize_t
        self.u.SetParent.argtypes = (w.HWND, w.HWND); self.u.SetParent.restype = w.HWND
        self.u.GetParent.argtypes = (w.HWND,); self.u.GetParent.restype = w.HWND
        self.u.GetWindow.argtypes = (w.HWND, w.UINT); self.u.GetWindow.restype = w.HWND
        self.u.GetWindowRect.argtypes = (w.HWND, ctypes.POINTER(w.RECT))
        self.u.ClientToScreen.argtypes = (w.HWND, ctypes.POINTER(w.POINT))
        self.u.IsWindow.argtypes = (w.HWND,)
        self.u.IsWindowVisible.argtypes = (w.HWND,)
        self.u.ShowWindow.argtypes = (w.HWND, ctypes.c_int)
        self.u.SetWindowPos.argtypes = (w.HWND, w.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, w.UINT)
        self.k.OpenProcess.argtypes = (w.DWORD, w.BOOL, w.DWORD); self.k.OpenProcess.restype = w.HANDLE
        self.k.QueryFullProcessImageNameW.argtypes = (w.HANDLE, w.DWORD, w.LPWSTR, ctypes.POINTER(w.DWORD))
        self.k.CloseHandle.argtypes = (w.HANDLE,)
        self.child = None
        self.old_style = self.old_parent = None
        self.hidden_tools = []
        stage.bind('<Configure>', lambda event: self.resize())

    def title(self, handle):
        value = self.ctypes.create_unicode_buffer(512)
        self.u.GetWindowTextW(handle, value, len(value))
        return value.value

    def sdk_process(self, handle):
        pid = self.w.DWORD()
        self.u.GetWindowThreadProcessId(handle, self.ctypes.byref(pid))
        process = self.k.OpenProcess(0x1000, False, pid.value)
        if not process:
            return False
        try:
            image = self.ctypes.create_unicode_buffer(32768)
            length = self.w.DWORD(len(image))
            return bool(self.k.QueryFullProcessImageNameW(process, 0, image, self.ctypes.byref(length))
                        and Path(image.value).is_relative_to(self.lab.sdk.resolve())
                        and Path(image.value).name.lower() == 'qemu-system-x86_64.exe')
        finally:
            self.k.CloseHandle(process)

    def attached(self):
        if self.child and self.u.IsWindow(self.child):
            return True
        self.child = None
        return False

    def attach(self, serial=None):
        if self.attached():
            if serial and not native_title_matches(self.title(self.child), serial):
                raise RuntimeError('The attached native window does not match the verified lab target.')
            return True
        matches = []
        @self.callback
        def visit(handle, extra):
            if native_title_matches(self.title(handle), serial) and self.sdk_process(handle):
                matches.append(handle)
            return True
        self.u.EnumWindows(visit, 0)
        if len(matches) > 1:
            if serial is None:  # Qt can expose transient startup windows before the VM is ready.
                return False
            raise RuntimeError('Multiple SDK windows match the lab. Close the extra lab instance.')
        if not matches:
            return False
        handle = matches[0]
        self.old_style = self.u.GetWindowLongPtrW(handle, -16)
        self.old_parent = self.u.GetParent(handle)
        # Remove the independent window frame; preserve native Qt client rendering.
        style = (self.old_style & ~0x80cf0000) | 0x46000000
        self.u.SetWindowLongPtrW(handle, -16, style)
        self.ctypes.set_last_error(0)
        self.u.SetParent(handle, self.stage.winfo_id())
        if self.u.GetParent(handle) != self.stage.winfo_id():
            self.u.SetWindowLongPtrW(handle, -16, self.old_style)
            raise RuntimeError('Windows could not attach the emulator display. Check process privilege/DPI settings.')
        self.child = handle
        self.u.ShowWindow(handle, 5)
        self.resize()
        return True

    def hide_toolbar(self):
        if not self.attached():
            return
        @self.callback
        def visit(handle, extra):
            # Hide only tool windows owned by this exact emulator client window.
            if (self.u.GetWindow(handle, 4) == self.child
                    and self.u.GetWindowLongPtrW(handle, -20) & 0x80
                    and self.u.IsWindowVisible(handle) and self.sdk_process(handle)):
                if handle not in self.hidden_tools:
                    self.hidden_tools.append(handle)
                self.u.ShowWindow(handle, 0)
            return True
        self.u.EnumWindows(visit, 0)

    def resize(self):
        if not self.attached():
            return
        p = self.lab.profile()
        width, height = self.stage.winfo_width(), self.stage.winfo_height()
        scale = min(1.0, width / p['width'], height / p['height'])
        w, h = max(1, int(p['width'] * scale)), max(1, int(p['height'] * scale))
        x, y = (width - w) // 2, (height - h) // 2
        bounds = self.w.RECT(); origin = self.w.POINT(0, 0)
        self.u.GetWindowRect(self.child, self.ctypes.byref(bounds))
        self.u.ClientToScreen(self.stage.winfo_id(), self.ctypes.byref(origin))
        actual = (bounds.left - origin.x, bounds.top - origin.y,
                  bounds.right - bounds.left, bounds.bottom - bounds.top)
        if actual != (x, y, w, h):
            self.u.SetWindowPos(self.child, None, x, y, w, h, 0x0034)
        self.hide_toolbar()

    def release(self):
        if self.attached():
            self.u.SetParent(self.child, self.old_parent)
            self.u.SetWindowLongPtrW(self.child, -16, self.old_style)
            self.u.ShowWindow(self.child, 5)
            for handle in self.hidden_tools:
                if self.u.IsWindow(handle):
                    self.u.ShowWindow(handle, 5)
        self.child = None
        self.hidden_tools.clear()


def native_title_matches(title: str, serial: str | None = None) -> bool:
    if not title.startswith('Android Emulator - '):
        return False
    port = str(EMULATOR_PORT) if serial is None else serial.removeprefix('emulator-')
    if serial is not None and not re.fullmatch(r'emulator-\d+', serial):
        return False
    return re.search(r'\b' + re.escape(AVD) + ':' + port + r'\b', title) is not None


def gui(lab: Lab):
    import ctypes
    import tkinter as tk
    from tkinter import ttk, filedialog

    if sys.platform == 'win32':
        try:
            api = ctypes.WinDLL('user32', use_last_error=True)
            api.SetProcessDpiAwarenessContext.argtypes = (ctypes.c_void_p,)
            api.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        except (AttributeError, OSError):
            pass
    window = tk.Tk()
    window.title('Rokid Android Lab')
    window.geometry(f'1280x{min(980, window.winfo_screenheight() - 90)}')
    window.minsize(1040, min(lab.profile()['height'] + 290, window.winfo_screenheight() - 70))
    frame = ttk.Frame(window, padding=12); frame.pack(fill='both', expand=True)
    heading = ttk.Frame(frame); heading.pack(fill='x', pady=(0, 8))
    ttk.Label(heading, text='Rokid Android Lab', font=('Segoe UI', 18, 'bold')).pack(side='left')
    profile = tk.StringVar(value=lab.describe())
    ttk.Label(heading, textvariable=profile).pack(side='right')
    panes = ttk.Panedwindow(frame, orient='horizontal'); panes.pack(fill='both', expand=True)
    left = ttk.Frame(panes, width=820); right = ttk.Frame(panes, width=360)
    panes.add(left, weight=3); panes.add(right, weight=1)
    left.columnconfigure(0, weight=1); left.rowconfigure(1, weight=1)
    power = ttk.Frame(left); power.grid(row=0, column=0, sticky='ew', pady=(0, 6))
    stage = tk.Frame(left, background='#090b0c', highlightthickness=1, highlightbackground='#30383d')
    stage.grid(row=1, column=0, sticky='nsew', padx=(0, 8))
    placeholder = tk.Label(stage, text='Start emulator\nThe virtual Android display appears here.',
                           fg='#aebbc2', bg='#090b0c', font=('Segoe UI', 15), justify='center')
    placeholder.place(relx=.5, rely=.5, anchor='center')
    host = NativeEmulatorHost(stage, lab)
    actions = ttk.Frame(left); actions.grid(row=2, column=0, sticky='ew', pady=(8, 4))
    input_area = ttk.Frame(left); input_area.grid(row=3, column=0, sticky='ew')
    status = tk.StringVar(value='Ready — virtual environment only.')
    ttk.Label(left, textvariable=status).grid(row=4, column=0, sticky='w', pady=(6, 0))

    notebook = ttk.Notebook(right); notebook.pack(fill='both', expand=True)
    lab_tab = ttk.Frame(notebook, padding=6); app_tab = ttk.Frame(notebook, padding=6)
    notebook.add(lab_tab, text='Lab'); notebook.add(app_tab, text='App log')
    lab_tab.columnconfigure(0, weight=1); lab_tab.rowconfigure(1, weight=1)
    lab_tools = ttk.Frame(lab_tab); lab_tools.grid(row=0, column=0, sticky='ew', pady=(0, 6))
    def console(parent):
        container = ttk.Frame(parent)
        container.columnconfigure(0, weight=1); container.rowconfigure(0, weight=1)
        text = tk.Text(container, wrap='none', font=('Consolas', 9), width=38)
        vertical = ttk.Scrollbar(container, orient='vertical', command=text.yview)
        horizontal = ttk.Scrollbar(container, orient='horizontal', command=text.xview)
        text.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        text.grid(row=0, column=0, sticky='nsew'); vertical.grid(row=0, column=1, sticky='ns')
        horizontal.grid(row=1, column=0, sticky='ew')
        return container, text
    lab_console, output = console(lab_tab); lab_console.grid(row=1, column=0, sticky='nsew')
    output.insert('end', 'Virtual Android development only.\n\nStart emulator → choose app → Build & run.\n'
                  'Use the mouse or the buttons below the screen.\n'
                  'Send file copies into Android Download.\n\nLab never pairs with, queries or controls real glasses.\n')
    app_tab.columnconfigure(0, weight=1); app_tab.rowconfigure(2, weight=1)
    log_header = ttk.Frame(app_tab); log_header.grid(row=0, column=0, sticky='ew', pady=(0, 4))
    app_log_label = tk.StringVar(value='paper-viewer')
    ttk.Label(log_header, textvariable=app_log_label).pack(side='left')
    auto_logs = tk.BooleanVar(value=True)
    ttk.Checkbutton(log_header, text='Auto', variable=auto_logs).pack(side='right')
    log_status = tk.StringVar(value='Recent selected-app log (up to 300 entries).')
    ttk.Label(app_tab, textvariable=log_status, wraplength=330).grid(row=1, column=0, sticky='w', pady=(0, 4))
    app_console, app_output = console(app_tab); app_console.grid(row=2, column=0, sticky='nsew')
    jobs = queue.Queue()
    controls = []
    busy = closing = close_requested = embedding_requested = False
    alive = True

    def report(message, error=False):
        output.insert('end', ('\nERROR: ' if error else '\n') + str(message) + '\n')
        output.see('end')
        if int(output.index('end-1c').split('.')[0]) > 1200:
            output.delete('1.0', '200.0')

    def submit(action, success=None):
        nonlocal busy
        if busy or closing:
            return
        busy = True
        status.set('Working…')
        for control in controls:
            control.configure(state='disabled')
        def worker():
            try:
                jobs.put((True, action(), success))
            except Exception as error:
                jobs.put((False, str(error), None))
        threading.Thread(target=worker, daemon=True).start()

    def button(parent, label, callback):
        control = ttk.Button(parent, text=label, command=callback)
        control.pack(side='left', padx=(0, 5), pady=3)
        controls.append(control)
        return control

    def attached(serial):
        nonlocal embedding_requested
        embedding_requested = True
        if serial and not host.attach(serial):
            embedding_requested = False
            raise RuntimeError('This VM has no native display (possibly headless). Use Stop, then Start emulator to attach it here.')
        if serial:
            embedding_requested = True
            placeholder.place_forget()
            host.resize()

    def start():
        nonlocal embedding_requested
        embedding_requested = True
        def boot():
            message = lab.start(embedded=True)
            return message, lab.target()
        submit(boot, lambda result: attached(result[1]))

    def stopped(result=None):
        nonlocal embedding_requested
        embedding_requested = False
        host.child = None
        placeholder.configure(text='Emulator stopped\nSaved apps and files are retained.')
        placeholder.place(relx=.5, rely=.5, anchor='center')

    selected = tk.StringVar(value='paper-viewer')
    selector = ttk.Combobox(actions, textvariable=selected, values=list(APPS), state='readonly', width=16)
    selector.pack(side='left', padx=(0, 8)); controls.append(selector)
    button(power, 'Start', start)
    button(power, 'Stop', lambda: submit(lab.stop, stopped))
    button(actions, 'Build & run', lambda: submit(lambda app=selected.get(): lab.launch(app, build=True)))
    button(actions, 'Run APK', lambda: submit(lambda app=selected.get(): lab.launch(app)))
    def send_file():
        source = filedialog.askopenfilename(parent=window, title='Send file to Android Download', filetypes=[('All files', '*')])
        if source:
            submit(lambda: lab.send_file(Path(source)))
    button(actions, 'Send file', send_file)

    pad = ttk.Frame(input_area); pad.pack(pady=3)
    for key, r, c in (('up', 0, 1), ('left', 1, 0), ('enter', 1, 1), ('right', 1, 2), ('down', 2, 1), ('back', 2, 3)):
        control = ttk.Button(pad, text=key.title(), width=9,
                             command=lambda key=key: submit(lambda: lab.key(key)))
        control.grid(row=r, column=c, padx=3, pady=2); controls.append(control)
    button(lab_tools, 'Check', lambda: submit(lab.doctor))
    button(lab_tools, 'Setup', lambda: submit(lab.setup))

    def display_settings():
        dialog = tk.Toplevel(window)
        dialog.title('Virtual display settings'); dialog.transient(window); dialog.grab_set()
        form = ttk.Frame(dialog, padding=16); form.pack(fill='both', expand=True)
        current = lab.profile()
        entries = {}
        for row, (name, label) in enumerate((('width', 'Width (px)'), ('height', 'Height (px)'),
                                             ('density', 'Density (dpi)'), ('fontScale', 'Font scale'))):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky='w', padx=(0, 14), pady=4)
            value = tk.StringVar(value=str(current[name])); entries[name] = value
            ttk.Entry(form, textvariable=value, width=16).grid(row=row, column=1, pady=4)
        error = tk.StringVar(value='Stop the virtual emulator before applying. API is fixed at 32.')
        ttk.Label(form, textvariable=error, wraplength=360).grid(row=4, column=0, columnspan=2, pady=10)
        def apply():
            try:
                values = (int(entries['width'].get()), int(entries['height'].get()),
                          int(entries['density'].get()), float(entries['fontScale'].get()))
                validate_profile(dict(api=32, width=values[0], height=values[1], density=values[2],
                                      fontScale=values[3], source='manual'))
            except ValueError as problem:
                error.set(str(problem)); return
            submit(lambda: lab.configure_display(*values), lambda result: dialog.destroy() if dialog.winfo_exists() else None)
        ttk.Button(form, text='Apply locally', command=apply).grid(row=5, column=0, pady=4)
        ttk.Button(form, text='Cancel', command=dialog.destroy).grid(row=5, column=1, pady=4)
    button(lab_tools, 'Display…', display_settings)

    log_jobs = queue.Queue()
    log_busy = False
    next_log_time = 0.0
    last_log_payload = None
    def request_logs():
        nonlocal log_busy, next_log_time
        if log_busy or closing or not alive:
            return
        app = selected.get()
        log_busy = True
        next_log_time = time.monotonic() + 2
        log_status.set('Reading virtual-app log…')
        def worker():
            try:
                log_jobs.put((app, True, lab.logs(app)))
            except Exception as problem:
                log_jobs.put((app, False, str(problem)))
        threading.Thread(target=worker, daemon=True).start()
    button(log_header, 'Refresh', request_logs)
    def app_changed(event=None):
        app_log_label.set(selected.get())
        if notebook.select() == str(app_tab):
            request_logs()
    selector.bind('<<ComboboxSelected>>', app_changed)
    notebook.bind('<<NotebookTabChanged>>', app_changed)
    def poll_logs():
        nonlocal log_busy, last_log_payload
        if not alive:
            return
        try:
            app, ok, payload = log_jobs.get_nowait()
        except queue.Empty:
            pass
        else:
            log_busy = False
            if app == selected.get():
                item = (app, ok, payload)
                if item != last_log_payload:
                    position = app_output.yview()
                    horizontal_position = app_output.xview()[0]
                    app_output.delete('1.0', 'end'); app_output.insert('end', payload)
                    if position[1] >= .99:
                        app_output.see('end')
                    else:
                        app_output.yview_moveto(position[0])
                    app_output.xview_moveto(horizontal_position)
                    last_log_payload = item
                log_status.set('Recent selected-app log (up to 300 entries).' if ok else 'App log unavailable')
        if (auto_logs.get() and notebook.select() == str(app_tab) and host.attached()
                and not busy and not closing and time.monotonic() >= next_log_time):
            request_logs()
        window.after(300, poll_logs)
    window.after(300, poll_logs)

    def finish_close():
        nonlocal alive
        # Do not destroy a parent window while another process is still its child.
        host.release()
        alive = False
        window.destroy()

    def close():
        nonlocal closing, close_requested, busy
        if closing:
            return
        if busy:
            close_requested = True
            status.set('Closing after the current operation finishes…')
            return
        if host.attached():
            def shutdown():
                return lab.stop()
            submit(shutdown, lambda result: finish_close())
            closing = True
            status.set('Closing the attached lab emulator…')
        else:
            finish_close()
    window.protocol('WM_DELETE_WINDOW', close)

    def poll():
        nonlocal busy, closing, embedding_requested
        try:
            ok, result, callback = jobs.get_nowait()
        except queue.Empty:
            pass
        else:
            try:
                if ok:
                    report(result[0] if isinstance(result, tuple) else result or 'Ready')
                    if callback:
                        callback(result)
                else:
                    report(result, error=True)
                    if closing:
                        finish_close()
                        return
                    if not host.attached():
                        embedding_requested = False
                status.set('Done' if ok else 'Needs attention')
            except Exception as error:
                report(error, error=True)
                embedding_requested = False
                status.set('Needs attention')
            if not alive:
                return
            profile.set(lab.describe())
            busy = False
            for control in controls:
                control.configure(state='readonly' if isinstance(control, ttk.Combobox) else 'normal')
            if close_requested:
                closing = False
                close()
                if not alive:
                    return
        if embedding_requested:
            try:
                if host.attach():
                    placeholder.place_forget()
                    host.resize()
            except Exception as error:
                report(error, error=True)
                embedding_requested = False
        window.after(250, poll)
    window.after(250, poll)
    # Reuse only our already running VM; do not start a new one just by opening the panel.
    window.after(300, lambda: submit(lambda: lab.target(required=False), attached))
    window.mainloop()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command')
    for name in ('gui', 'doctor', 'setup', 'stop'):
        commands.add_parser(name)
    start = commands.add_parser('start'); start.add_argument('--headless', action='store_true'); start.add_argument('--embedded', action='store_true')
    display = commands.add_parser('display')
    display.add_argument('--width', type=int, required=True)
    display.add_argument('--height', type=int, required=True)
    display.add_argument('--density', type=int, required=True)
    display.add_argument('--font-scale', type=float, default=1.0)
    launch = commands.add_parser('run'); launch.add_argument('app', choices=APPS); launch.add_argument('--build', action='store_true')
    key = commands.add_parser('key'); key.add_argument('name', choices=KEYS, help='Buttons mode: arrows/enter/back. PC-only debug extras: tab/page-up/page-down.')
    transfer = commands.add_parser('file'); transfer.add_argument('path', type=Path)
    logs = commands.add_parser('logs'); logs.add_argument('app', choices=APPS)
    args = parser.parse_args()
    lab = Lab()
    if not args.command or args.command == 'gui':
        gui(lab)
    elif args.command == 'display':
        print(lab.configure_display(args.width, args.height, args.density, args.font_scale))
    elif args.command == 'start':
        print(lab.start(args.headless, args.embedded))
    elif args.command == 'run':
        print(lab.launch(args.app, args.build))
    elif args.command == 'key':
        print(lab.key(args.name))
    elif args.command == 'file':
        print(lab.send_file(args.path))
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
