# GharBeka

> **"We Rotate Problems. You Pay to Unrotate Them."**

**GharBeka** is a satirical desktop subscription-software parody for Windows 10 and Windows 11. The application playfully parodies predatory SaaS subscription tiers by charging users fictional subscriptions to "unrotate" a sideways screen.

- **Current Version**: `1.0.0`
- **Target Platform**: Windows 10 and Windows 11 (64-bit)
- **Primary Release Executable**: `dist/GharBeka.exe` (Standalone One-File Executable)
- **Diagnostic Distribution**: `dist/GharBeka_onedir/` (One-Directory Bundle)

---

## Important Disclaimers & Parody Notice

> [!NOTE]
> **Fictional Subscription Parody**: GharBeka is satire. No real payment processing, credit card collection, or recurring subscriptions exist. All checkout flows, tier upgrades, and checkout buttons are purely simulated local UI demonstrations.

> [!WARNING]
> **Hardware & Display Behavior**: Actual display changes in "Real Display Mode" depend on Microsoft Windows display subsystem drivers and GPU capabilities. Simulation Mode is enabled by default. Automated tests never rotate physical monitors.

> [!IMPORTANT]
> **Signing & Security Notice**: The release executable is not digitally signed with a commercial EV certificate. When launched on Windows SmartScreen, you may need to click "More info" -> "Run anyway". Universal compatibility across all OEM graphics drivers cannot be guaranteed.

---

## Packaging Strategy: One-File vs. One-Directory

GharBeka provides two packaging formats generated via PyInstaller 6.22+:

| Format | Distribution Path | Description | Recommended Usage |
| :--- | :--- | :--- | :--- |
| **One-File (`--onefile`)** | `dist/GharBeka.exe` | Single self-contained executable (~44.6 MB) embedding the Python runtime, PySide6 Qt libraries, application code, and icons. Upon launch, it unpacks necessary runtime dependencies to a secure temporary directory (`%LOCALAPPDATA%\Temp\_MEIxxxxxx`). | **Standard End-User Distribution**. End users can run this single file without needing Python installed. |
| **One-Directory (`--onedir`)** | `dist/GharBeka_onedir/` | Unpacked application folder containing `GharBeka_diag.exe` and an `_internal/` directory with discrete DLLs and Qt platform plugins (`qwindows.dll`). | **Diagnostic & Troubleshooting Release**. Ideal for inspecting loaded Qt plugins, resolving system DLL incompatibilities, or debugging startup issues without temporary extraction overhead. |

---

## Project Structure

```
GharBeka/
├── main.py                     # Application entry point with logging & crash handler
├── requirements.txt            # Project dependencies (PySide6, pytest, pyinstaller)
├── GharBeka.spec               # PyInstaller build specification (onefile + onedir)
├── version_info.txt            # Windows PE version metadata (Version 1.0.0)
├── README.md                   # Product documentation, release notes & safety guide
├── assets/
│   ├── icon.ico                # Multi-resolution Windows application icon (16x16 to 256x256)
│   └── icon.png                # High-resolution raster icon (256x256)
├── scripts/
│   ├── build_windows.bat       # Automated clean build script
│   ├── run_tests.bat           # Automated pytest suite runner
│   ├── generate_icon.py        # Native icon generator using PySide6
│   └── verify_release.py       # Post-build PE metadata & execution verifier
├── src/
│   ├── __init__.py             # Package marker
│   ├── dialogs.py              # Modal dialogs (Subscription, Checkout, Settings)
│   ├── display_controller.py   # Isolated Win32 display API controller
│   ├── main_window.py          # Main window layout, monitor widget, interaction handlers
│   ├── recovery_manager.py     # Automatic countdown timer & global hotkey manager
│   ├── runtime.py              # Resource path resolution, logging & persistent settings
│   └── styles.py               # Dark SaaS theme palette and Qt Style Sheets (QSS)
└── tests/
    └── test_app.py             # 37 automated unit tests covering all features & workflows
```

---

## Installation & Setup

### Prerequisites
- Microsoft Windows 10 or Windows 11 (64-bit)
- Python 3.10+ (tested on Python 3.13.2 64-bit)
- Windows display adapter supporting standard display modes

### Install Development Dependencies

```powershell
pip install -r requirements.txt
```

---

## Running the Application

### 1. From Python Source

```powershell
python main.py
```

### 2. From Packaged Windows Executable

Double-click `dist\GharBeka.exe` or execute from PowerShell / Command Prompt:

```powershell
.\dist\GharBeka.exe
```

No separate Python installation or virtual environment is required for end users running `dist\GharBeka.exe`.

---

## Automated Build & Verification Workflow

### 1. Run Automated Unit Tests

To run the full suite of 37 automated tests:

```powershell
.\scripts\run_tests.bat
```

All unit tests execute in headless/offscreen mode (`QT_QPA_PLATFORM=offscreen`) and will never alter the physical display orientation.

### 2. Build the Windows Executable

To build both `dist/GharBeka.exe` and `dist/GharBeka_onedir/`:

```powershell
.\scripts\build_windows.bat
```

The build script will:
1. Verify execution on Microsoft Windows.
2. Verify the Python runtime.
3. Validate requirements from `requirements.txt`.
4. Run the 37 automated unit tests (aborting immediately if any test fails).
5. Generate fresh multi-resolution application icons (`assets/icon.ico`, `assets/icon.png`).
6. Safely clean stale build artifacts.
7. Run PyInstaller to package the binaries.
8. Verify that output executables exist and are valid.

### 3. Verify the Packaged Release

To run post-build release verification checks:

```powershell
python scripts\verify_release.py
```

This verifies executable presence, PE version metadata, Qt platform plugins, live process execution, clean shutdown, and diagnostic log creation.

---

## Configuration & Diagnostic Logs

GharBeka stores settings and diagnostic logs in a predictable, user-writable directory:

- **Data Directory**: `%LOCALAPPDATA%\GharBeka\` (e.g. `C:\Users\<User>\AppData\Local\GharBeka\`)
- **Diagnostic Log**: `%LOCALAPPDATA%\GharBeka\gharbeka.log`
- **Settings INI**: `%LOCALAPPDATA%\GharBeka\settings.ini`

### Diagnostic Log Inspection
If the application encounters an issue or unexpected behavior, open `gharbeka.log` in Notepad:

```powershell
notepad "$env:LOCALAPPDATA\GharBeka\gharbeka.log"
```

The log records application startup details, frozen executable flags, resource base paths, rotation attempts, safety timer activations, recovery triggers, and error traces.

---

## Safety System & Emergency Recovery

GharBeka incorporates an automatic recovery and safety architecture to prevent accidental physical monitor misconfiguration:

1. **Simulation Mode Default**: The app always starts in Simulation Mode. Physical display changes require explicit opt-in in Settings.
2. **Auto-Recovery Countdown**: Whenever a rotation occurs, a non-blocking safety timer (configurable to 15s, 30s, 60s default, or 120s) ticks down in real time. If unconfirmed, the screen automatically restores to 0° landscape.
3. **Un-Gated Emergency Recovery**: Clicking "Emergency Recovery" immediately restores original display orientation without triggering any subscription checks.
4. **Global Windows Emergency Hotkey (`Ctrl+Alt+Shift+R`)**: A native Win32 `RegisterHotKey` hook restores display orientation even if the GharBeka window loses focus.
5. **Clean Exit Recovery**: Orderly application shutdown (`closeEvent`) automatically attempts restoration before closing.
6. **Manual Windows Fallback**: If hardware fails to restore, press `Win+I` -> **System** -> **Display** -> **Display orientation** -> select **Landscape**.

---

## Supported and Tested Environments

- **Tested Environment**: Windows 11 Enterprise / Pro 64-bit (Build 26220), Python 3.13.2, PySide6 6.12.0, PyInstaller 6.22.3.
- **Supported Platforms**: Windows 10 (64-bit) and Windows 11 (64-bit).
- **Unverified Platforms**: Windows 7/8 (unsupported by Python 3.11+ and modern Qt), 32-bit Windows, Windows on ARM without x64 emulation, and multi-GPU virtualized display configurations.

---

## Known Limitations

- Real Display Mode requires a standard Windows display adapter supporting the Win32 `ChangeDisplaySettingsExW` API. Certain virtual machines or headless display drivers may report unsupported graphics modes.
- Binary is self-contained and unsigned; Windows Defender SmartScreen may display a warning on initial launch on untrusted machines.
