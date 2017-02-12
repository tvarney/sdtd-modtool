
import os
import os.path


def _get_steam_path_windows():
    import winreg

    root = winreg.HKEY_CURRENT_USER
    path = "SOFTWARE\\Valve\\Steam"
    key = "SteamPath"

    value = ""
    try:
        hkey = winreg.OpenKeyEx(root, path)
        value = winreg.QueryValueEx(hkey, key)[0]
    except FileNotFoundError:
        return None
    except OSError:
        return None
    return value


def _get_steam_path_invalid():
    return None

_get_steam_path_impl = _get_steam_path_invalid
if os.name == 'nt':
    _get_steam_path_impl = _get_steam_path_windows


def get_steam_path():
    return _get_steam_path_impl()


def get_sdtd_path():
    root = get_steam_path()
    if root is None or not os.path.exists(root):
        return None

    sdtd_path = os.path.join(root, "steamapps/common/7 Days To Die/Data/Config")
    if os.path.exists(sdtd_path):
        return sdtd_path
    return None

