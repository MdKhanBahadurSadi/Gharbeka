"""Windows Display Controller for GharBeka Phase 3.

Provides isolated Win32 display API integration for detecting displays,
checking orientation support, applying screen rotation, and restoring saved modes.
"""

import sys
import ctypes
from ctypes import wintypes
from typing import Any

# Win32 Display Constants
ENUM_CURRENT_SETTINGS = -1
ENUM_REGISTRY_SETTINGS = -2

DMDO_DEFAULT = 0  # 0 degrees (Landscape)
DMDO_90 = 1       # 90 degrees (Portrait)
DMDO_180 = 2      # 180 degrees (Landscape Flipped)
DMDO_270 = 3      # 270 degrees (Portrait Flipped)

DM_DISPLAYORIENTATION = 0x00080000
DM_PELSWIDTH = 0x00080000
DM_PELSHEIGHT = 0x00100000

DISP_CHANGE_SUCCESSFUL = 0
DISP_CHANGE_RESTART = 1
DISP_CHANGE_FAILED = -1
DISP_CHANGE_BADMODE = -2
DISP_CHANGE_NOTUPDATED = -3
DISP_CHANGE_BADFLAGS = -4
DISP_CHANGE_BADPARAM = -5

CDS_UPDATEREGISTRY = 0x00000001
CDS_TEST = 0x00000002
CDS_FULLSCREEN = 0x00000004

DISPLAY_DEVICE_ATTACHED_TO_DESKTOP = 0x00000001
DISPLAY_DEVICE_PRIMARY_DEVICE = 0x00000004


class POINTL(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


class _DUMMYSTRUCT1(ctypes.Structure):
    _fields_ = [
        ("dmOrientation", wintypes.SHORT),
        ("dmPaperSize", wintypes.SHORT),
        ("dmPaperLength", wintypes.SHORT),
        ("dmPaperWidth", wintypes.SHORT),
        ("dmScale", wintypes.SHORT),
        ("dmCopies", wintypes.SHORT),
        ("dmDefaultSource", wintypes.SHORT),
        ("dmPrintQuality", wintypes.SHORT),
    ]


class _DUMMYSTRUCT2(ctypes.Structure):
    _fields_ = [
        ("dmPosition", POINTL),
        ("dmDisplayOrientation", wintypes.DWORD),
        ("dmDisplayFixedOutput", wintypes.DWORD),
    ]


class _DUMMYUNION1(ctypes.Union):
    _fields_ = [
        ("s1", _DUMMYSTRUCT1),
        ("s2", _DUMMYSTRUCT2),
    ]


class DEVMODEW(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", wintypes.WCHAR * 32),
        ("dmSpecVersion", wintypes.WORD),
        ("dmDriverVersion", wintypes.WORD),
        ("dmSize", wintypes.WORD),
        ("dmDriverExtra", wintypes.WORD),
        ("dmFields", wintypes.DWORD),
        ("u1", _DUMMYUNION1),
        ("dmColor", wintypes.SHORT),
        ("dmDuplex", wintypes.SHORT),
        ("dmYResolution", wintypes.SHORT),
        ("dmTTOption", wintypes.SHORT),
        ("dmCollate", wintypes.SHORT),
        ("dmFormName", wintypes.WCHAR * 32),
        ("dmLogPixels", wintypes.WORD),
        ("dmBitsPerPel", wintypes.DWORD),
        ("dmPelsWidth", wintypes.DWORD),
        ("dmPelsHeight", wintypes.DWORD),
        ("dmDisplayFlags", wintypes.DWORD),
        ("dmDisplayFrequency", wintypes.DWORD),
        ("dmICMMethod", wintypes.DWORD),
        ("dmICMIntent", wintypes.DWORD),
        ("dmMediaType", wintypes.DWORD),
        ("dmDitherType", wintypes.DWORD),
        ("dmReserved1", wintypes.DWORD),
        ("dmReserved2", wintypes.DWORD),
        ("dmPanningWidth", wintypes.DWORD),
        ("dmPanningHeight", wintypes.DWORD),
    ]


class DISPLAY_DEVICEW(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("DeviceName", wintypes.WCHAR * 32),
        ("DeviceString", wintypes.WCHAR * 128),
        ("StateFlags", wintypes.DWORD),
        ("DeviceID", wintypes.WCHAR * 128),
        ("DeviceKey", wintypes.WCHAR * 128),
    ]


def interpret_cds_error(code: int) -> str:
    """Return human-readable message for Windows ChangeDisplaySettings error code."""
    errors = {
        DISP_CHANGE_SUCCESSFUL: "Success",
        DISP_CHANGE_RESTART: "Computer restart required for changes to take effect",
        DISP_CHANGE_FAILED: "The display driver failed the specified graphics mode",
        DISP_CHANGE_BADMODE: "Graphics mode is not supported by display driver or hardware",
        DISP_CHANGE_NOTUPDATED: "Unable to write settings to Windows registry",
        DISP_CHANGE_BADFLAGS: "Invalid set of flags passed to display API",
        DISP_CHANGE_BADPARAM: "Invalid parameter passed to display API",
    }
    return errors.get(code, f"Unknown Windows display API error code ({code})")


class DisplayController:
    """Controller managing Windows display device enumeration, mode query, and rotation."""

    def __init__(self) -> None:
        self._saved_original_modes: dict[str, DEVMODEW] = {}

    @staticmethod
    def is_windows() -> bool:
        """Check if executing on a Microsoft Windows environment."""
        return sys.platform == "win32"

    def get_user32(self) -> Any:
        """Get user32 DLL if running on Windows."""
        if not self.is_windows():
            return None
        return getattr(ctypes.windll, "user32", None)

    def get_display_devices(self) -> list[dict[str, Any]]:
        """Enumerate active connected desktop display devices."""
        user32 = self.get_user32()
        if user32 is None:
            return [
                {
                    "device_name": r"\\.\DISPLAY1",
                    "device_string": "Non-Windows Simulation Display",
                    "is_primary": True,
                    "is_active": True,
                }
            ]

        devices: list[dict[str, Any]] = []
        dev = DISPLAY_DEVICEW()
        dev.cb = ctypes.sizeof(DISPLAY_DEVICEW)
        i = 0

        while user32.EnumDisplayDevicesW(None, i, ctypes.byref(dev), 0):
            if dev.StateFlags & DISPLAY_DEVICE_ATTACHED_TO_DESKTOP:
                is_primary = bool(dev.StateFlags & DISPLAY_DEVICE_PRIMARY_DEVICE)
                devices.append(
                    {
                        "device_name": str(dev.DeviceName),
                        "device_string": str(dev.DeviceString),
                        "is_primary": is_primary,
                        "is_active": True,
                    }
                )
            i += 1

        if not devices:
            devices.append(
                {
                    "device_name": r"\\.\DISPLAY1",
                    "device_string": "Fallback Default Display",
                    "is_primary": True,
                    "is_active": True,
                }
            )

        return devices

    def get_primary_device_name(self) -> str:
        """Get the device identifier for the primary desktop display."""
        for dev in self.get_display_devices():
            if dev.get("is_primary"):
                return str(dev["device_name"])
        return r"\\.\DISPLAY1"

    def get_display_orientation(self, device_name: str | None = None) -> int:
        """Read the current display orientation for specified device (0, 1, 2, or 3)."""
        if device_name is None:
            device_name = self.get_primary_device_name()

        user32 = self.get_user32()
        if user32 is None:
            return DMDO_DEFAULT

        dm = DEVMODEW()
        dm.dmSize = ctypes.sizeof(DEVMODEW)

        res = user32.EnumDisplaySettingsW(
            device_name, ENUM_CURRENT_SETTINGS, ctypes.byref(dm)
        )
        if not res:
            raise RuntimeError(
                f"EnumDisplaySettingsW failed to query display '{device_name}'."
            )

        return int(dm.u1.s2.dmDisplayOrientation)

    def is_orientation_supported(
        self, device_name: str | None, target_orientation: int
    ) -> tuple[bool, str]:
        """Check if target orientation is supported by hardware/driver using CDS_TEST."""
        if device_name is None:
            device_name = self.get_primary_device_name()

        if target_orientation not in (DMDO_DEFAULT, DMDO_90, DMDO_180, DMDO_270):
            return False, f"Invalid target orientation code {target_orientation}."

        user32 = self.get_user32()
        if user32 is None:
            return True, "Simulation Mode: Orientation supported."

        dm = DEVMODEW()
        dm.dmSize = ctypes.sizeof(DEVMODEW)
        res = user32.EnumDisplaySettingsW(
            device_name, ENUM_CURRENT_SETTINGS, ctypes.byref(dm)
        )
        if not res:
            return False, f"Could not read display mode for '{device_name}'."

        current_orient = dm.u1.s2.dmDisplayOrientation
        test_dm = DEVMODEW()
        test_dm.dmSize = ctypes.sizeof(DEVMODEW)
        user32.EnumDisplaySettingsW(
            device_name, ENUM_CURRENT_SETTINGS, ctypes.byref(test_dm)
        )

        if (current_orient % 2) != (target_orientation % 2):
            test_dm.dmPelsWidth, test_dm.dmPelsHeight = (
                dm.dmPelsHeight,
                dm.dmPelsWidth,
            )

        test_dm.u1.s2.dmDisplayOrientation = target_orientation
        test_dm.dmFields |= (
            DM_DISPLAYORIENTATION | DM_PELSWIDTH | DM_PELSHEIGHT
        )

        cds_res = user32.ChangeDisplaySettingsExW(
            device_name, ctypes.byref(test_dm), None, CDS_TEST, None
        )
        if cds_res == DISP_CHANGE_SUCCESSFUL:
            return True, f"Orientation {target_orientation} is supported."
        else:
            return False, interpret_cds_error(cds_res)

    def rotate_display(
        self,
        device_name: str | None,
        target_orientation: int,
        persist: bool = False,
    ) -> tuple[bool, str]:
        """Apply target display orientation to the specified display device."""
        if device_name is None:
            device_name = self.get_primary_device_name()

        if not self.is_windows():
            return False, "Real display rotation requires Microsoft Windows."

        user32 = self.get_user32()
        if user32 is None:
            return False, "Windows user32 API unavailable."

        # Verify device is active
        active_devices = [d["device_name"] for d in self.get_display_devices()]
        if device_name not in active_devices:
            return (
                False,
                f"Target display '{device_name}' is no longer connected or available.",
            )

        # Query current mode and save original if not saved yet
        current_dm = DEVMODEW()
        current_dm.dmSize = ctypes.sizeof(DEVMODEW)
        if not user32.EnumDisplaySettingsW(
            device_name, ENUM_CURRENT_SETTINGS, ctypes.byref(current_dm)
        ):
            return False, f"Failed to query display settings for '{device_name}'."

        if device_name not in self._saved_original_modes:
            saved = DEVMODEW()
            saved.dmSize = ctypes.sizeof(DEVMODEW)
            user32.EnumDisplaySettingsW(
                device_name, ENUM_CURRENT_SETTINGS, ctypes.byref(saved)
            )
            self._saved_original_modes[device_name] = saved

        curr_orient = current_dm.u1.s2.dmDisplayOrientation
        if curr_orient == target_orientation:
            return (
                True,
                f"Display '{device_name}' is already at orientation {target_orientation}.",
            )

        supported, reason = self.is_orientation_supported(
            device_name, target_orientation
        )
        if not supported:
            return (
                False,
                f"Target orientation {target_orientation} unsupported on '{device_name}': {reason}",
            )

        new_dm = DEVMODEW()
        new_dm.dmSize = ctypes.sizeof(DEVMODEW)
        user32.EnumDisplaySettingsW(
            device_name, ENUM_CURRENT_SETTINGS, ctypes.byref(new_dm)
        )

        if (curr_orient % 2) != (target_orientation % 2):
            new_dm.dmPelsWidth, new_dm.dmPelsHeight = (
                current_dm.dmPelsHeight,
                current_dm.dmPelsWidth,
            )

        new_dm.u1.s2.dmDisplayOrientation = target_orientation
        new_dm.dmFields |= DM_DISPLAYORIENTATION | DM_PELSWIDTH | DM_PELSHEIGHT

        flags = CDS_UPDATEREGISTRY if persist else 0
        res = user32.ChangeDisplaySettingsExW(
            device_name, ctypes.byref(new_dm), None, flags, None
        )

        if res != DISP_CHANGE_SUCCESSFUL:
            return False, f"ChangeDisplaySettingsExW failed: {interpret_cds_error(res)}"

        actual_orient = self.get_display_orientation(device_name)
        if actual_orient != target_orientation:
            return (
                False,
                f"Display API reported success, but actual orientation ({actual_orient}) differs from requested ({target_orientation}).",
            )

        return (
            True,
            f"Display '{device_name}' successfully rotated to orientation {target_orientation}.",
        )

    def restore_original_orientation(
        self, device_name: str | None = None
    ) -> tuple[bool, str]:
        """Restore saved original display mode for specified device."""
        if device_name is None:
            device_name = self.get_primary_device_name()

        if not self.is_windows():
            return False, "Real display recovery requires Microsoft Windows."

        user32 = self.get_user32()
        if user32 is None:
            return False, "Windows user32 API unavailable."

        if device_name in self._saved_original_modes:
            saved_dm = self._saved_original_modes[device_name]
            res = user32.ChangeDisplaySettingsExW(
                device_name, ctypes.byref(saved_dm), None, 0, None
            )
            if res == DISP_CHANGE_SUCCESSFUL:
                return (
                    True,
                    f"Original display mode for '{device_name}' successfully restored.",
                )
            else:
                return (
                    False,
                    f"Failed to restore original mode for '{device_name}': {interpret_cds_error(res)}",
                )
        else:
            return self.rotate_display(device_name, DMDO_DEFAULT)

    def get_saved_original_orientation(self, device_name: str | None = None) -> int | None:
        """Return original orientation if saved in memory."""
        if device_name is None:
            device_name = self.get_primary_device_name()

        if device_name in self._saved_original_modes:
            return int(
                self._saved_original_modes[device_name].u1.s2.dmDisplayOrientation
            )
        return None
