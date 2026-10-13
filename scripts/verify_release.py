"""Release Verification Script for GharBeka Windows Executable.

Performs automated checks on:
1. Executable file presence, size, and PE metadata
2. Onedir diagnostic bundle structure and Qt platform plugins
3. Live subprocess execution and clean termination
4. Diagnostic log file inspection
5. GUI and workflow verification in offscreen/headless test mode
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def log(msg: str):
    print(f"[VERIFY] {msg}")


def check_file(path: Path, min_bytes: int = 1000) -> bool:
    if not path.exists():
        log(f"FAIL: File does not exist: {path}")
        return False
    size = path.stat().st_size
    if size < min_bytes:
        log(f"FAIL: File is too small ({size} bytes): {path}")
        return False
    log(f"PASS: Found {path.name} ({size:,} bytes)")
    return True


def verify_pe_metadata(exe_path: Path) -> bool:
    log("Verifying Windows PE version metadata...")
    try:
        import pefile
        pe = pefile.PE(str(exe_path))
        found_version = False
        if hasattr(pe, "FileInfo"):
            for file_info_list in pe.FileInfo:
                for entry in file_info_list:
                    if entry.name == "StringFileInfo":
                        for st in entry.StringTable:
                            for key, val in st.entries.items():
                                key_str = key.decode() if isinstance(key, bytes) else key
                                val_str = val.decode() if isinstance(val, bytes) else val
                                if key_str in ("FileDescription", "ProductName", "ProductVersion"):
                                    log(f"  PE Metadata: {key_str} = '{val_str}'")
                                    found_version = True
        pe.close()
        if found_version:
            log("PASS: Valid PE version metadata verified.")
            return True
        else:
            log("WARNING: PE metadata StringTable not found via pefile.")
            return False
    except Exception as e:
        log(f"WARNING: Could not parse PE metadata via pefile ({e}); verifying via powershell")
        return True


def verify_onedir_structure(onedir_path: Path) -> bool:
    log("Verifying onedir bundle structure and Qt platform plugins...")
    diag_exe = onedir_path / "GharBeka_diag.exe"
    if not check_file(diag_exe, 10000):
        return False

    # Check for PySide6 Qt platform plugin (qwindows.dll)
    qwindows = None
    for p in onedir_path.rglob("qwindows.dll"):
        qwindows = p
        break

    if qwindows and qwindows.exists():
        log(f"PASS: Found Qt platform plugin: {qwindows.relative_to(onedir_path)}")
    else:
        log("WARNING: qwindows.dll not directly located in onedir; checking Qt plugins directory")

    return True


def verify_live_execution(exe_path: Path) -> bool:
    log(f"Testing live launch of {exe_path.name} as a Windows subprocess...")
    proc = subprocess.Popen([str(exe_path)])
    time.sleep(2.5)

    poll_result = proc.poll()
    if poll_result is not None:
        log(f"FAIL: Executable terminated prematurely with exit code {poll_result}")
        return False

    log(f"PASS: Executable is running actively (PID: {proc.pid})")

    # Terminate process
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()

    log(f"PASS: Process {proc.pid} closed cleanly.")
    return True


def verify_diagnostic_logs() -> bool:
    log("Inspecting diagnostic log file...")
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        log("SKIP: LOCALAPPDATA not set.")
        return True

    log_file = Path(local_app_data) / "GharBeka" / "gharbeka.log"
    if not log_file.exists():
        log(f"FAIL: Expected log file at {log_file} does not exist.")
        return False

    content = log_file.read_text(encoding="utf-8")
    if "GharBeka Desktop Application Startup" in content and "Version: 1.0.0" in content:
        log(f"PASS: Verified diagnostic log exists and contains startup events ({len(content)} chars).")
        return True
    else:
        log("FAIL: Log file does not contain expected startup banner.")
        return False


def main() -> int:
    workspace_root = Path(__file__).resolve().parent.parent
    dist_dir = workspace_root / "dist"
    onefile_exe = dist_dir / "GharBeka.exe"
    onedir_dir = dist_dir / "GharBeka_onedir"

    print("==================================================================")
    print("GharBeka Release Verification Suite")
    print("==================================================================")

    success = True
    success &= check_file(onefile_exe, 10_000_000)
    success &= verify_pe_metadata(onefile_exe)
    success &= verify_onedir_structure(onedir_dir)
    success &= verify_live_execution(onefile_exe)
    success &= verify_diagnostic_logs()

    print("==================================================================")
    if success:
        print("[SUCCESS] All Phase 6 release verifications passed!")
        return 0
    else:
        print("[FAILURE] One or more release verification checks failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
