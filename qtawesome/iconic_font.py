r"""

Iconic Font
===========

A lightweight module handling iconic fonts.

It is designed to provide a simple way for creating QIcons from glyphs.

From a user's viewpoint, the main entry point is the ``IconicFont`` class which
contains methods for loading new iconic fonts with their character map and
methods returning instances of ``QIcon``.

"""

# Standard library imports
import ctypes
import json
import os
import shutil

# Third party imports
from PySide6.QtCore import (QObject)
from PySide6.QtGui import (QFont, QFontDatabase, QGuiApplication)

try:
    # Needed since `QGlyphRun` is not available for PySide2
    # See spyder-ide/qtawesome#210
    from PySide6.QtGui import QGlyphRun
except ImportError:
    QGlyphRun = None

# Linux packagers, please set this to True if you want to make qtawesome
# use system fonts
SYSTEM_FONTS = False

# Needed imports and constants to install bundled fonts on Windows
# Based on https://stackoverflow.com/a/41841088/15954282
if os.name == 'nt':
    from ctypes import wintypes
    import winreg

    user32 = ctypes.WinDLL('user32', use_last_error=True)
    gdi32 = ctypes.WinDLL('gdi32', use_last_error=True)

    FONTS_REG_PATH = r'Software\Microsoft\Windows NT\CurrentVersion\Fonts'
    GFRI_DESCRIPTION = 1
    GFRI_ISTRUETYPE = 3

    if not hasattr(wintypes, 'LPDWORD'):
        wintypes.LPDWORD = ctypes.POINTER(wintypes.DWORD)

    user32.SendMessageTimeoutW.restype = wintypes.LPVOID
    user32.SendMessageTimeoutW.argtypes = (
        wintypes.HWND,  # hWnd
        wintypes.UINT,  # Msg
        wintypes.LPVOID,  # wParam
        wintypes.LPVOID,  # lParam
        wintypes.UINT,  # fuFlags
        wintypes.UINT,  # uTimeout
        wintypes.LPVOID)  # lpdwResult

    gdi32.AddFontResourceW.argtypes = (
        wintypes.LPCWSTR,)  # lpszFilename

    # http://www.undocprint.org/winspool/getfontresourceinfo
    gdi32.GetFontResourceInfoW.argtypes = (
        wintypes.LPCWSTR,  # lpszFilename
        wintypes.LPDWORD,  # cbBuffer
        wintypes.LPVOID,  # lpBuffer
        wintypes.DWORD)  # dwQueryType


class FontError(Exception):
    """Exception for font errors."""


class IconicFont(QObject):
    """Main class for managing iconic fonts."""

    def __init__(self, *args):
        """IconicFont Constructor.

        Parameters
        ----------
        ``*args``: tuples
            Each positional argument is a tuple of 3 or 4 values:
            - The prefix string to be used when accessing a given font set,
            - The ttf font filename,
            - The json charmap filename,
            - Optionally, the directory containing these files. When not
              provided, the files will be looked for in the QtAwesome ``fonts``
              directory.
        """
        super().__init__()
        self.fontname = {}
        self.fontdata = {}
        self.fontids = {}
        self.charmap = {}
        self.icon_cache = {}
        self.rawfont_cache = {}
        for fargs in args:
            self.load_font(*fargs)

    def load_font(self, prefix, ttf_filename, charmap_filename, directory=None):
        """Loads a font file and the associated charmap.

        If ``directory`` is None, the files will be looked for in
        the qtawesome ``fonts`` directory.

        Parameters
        ----------
        prefix: str
            Prefix string to be used when accessing a given font set
        ttf_filename: str
            Ttf font filename
        charmap_filename: str
            Charmap filename
        directory: str or None, optional
            Directory path for font and charmap files
        """

        def hook(obj):
            result = {}
            for key in obj:
                try:
                    result[key] = chr(int(obj[key], 16))
                except ValueError:
                    if int(obj[key], 16) > 0xffff:
                        # ignoring unsupported code in Python 2.7 32bit Windows
                        # ValueError: chr() arg not in range(0x10000)
                        pass
                    else:
                        raise FontError(u'Failed to load character '
                                        '{0}:{1}'.format(key, obj[key]))
            return result

        if directory is None:
            directory = self._get_fonts_directory()

        # Load font
        if QGuiApplication.instance() is not None:
            with open(os.path.join(directory, ttf_filename), 'rb') as font_data:
                data = font_data.read()
                id_ = QFontDatabase.addApplicationFontFromData(data)
            font_data.close()

            loadedFontFamilies = QFontDatabase.applicationFontFamilies(id_)

            if loadedFontFamilies:
                self.fontids[prefix] = id_
                self.fontname[prefix] = loadedFontFamilies[0]
                self.fontdata[prefix] = data
            else:
                raise FontError(u"Font at '{0}' appears to be empty. "
                                "If you are on Windows 10, please read "
                                "https://support.microsoft.com/"
                                "en-us/kb/3053676 "
                                "to know how to prevent Windows from blocking "
                                "the fonts that come with QtAwesome.".format(os.path.join(directory, ttf_filename)))

            with open(os.path.join(directory, charmap_filename), 'r') as codes:
                self.charmap[prefix] = json.load(codes, object_hook=hook)

    def _get_prefix_chars(self, names):
        chars = []
        prefix = None
        for name in names:
            if '.' in name:
                prefix, n = name.split('.')
                if prefix in self.charmap:
                    if n in self.charmap[prefix]:
                        chars.append(self.charmap[prefix][n])
                    else:
                        error = 'Invalid icon name "{0}" in font "{1}"'.format(
                            n, prefix)
                        raise Exception(error)
                else:
                    error = 'Invalid font prefix "{0}"'.format(prefix)
                    raise Exception(error)
            else:
                raise Exception('Invalid icon name')

        return prefix, chars

    def font(self, prefix, size):
        """Return a QFont corresponding to the given prefix and size."""
        font = QFont()
        font.setFamily(self.fontname[prefix])
        font.setPixelSize(round(size))
        if prefix[-1] == 's':  # solid style
            font.setStyleName('Solid')
        return font

    def _get_fonts_directory(self):
        """
        Get bundled fonts directory.

        On Windows an attempt to install the fonts per user is done
        to prevent errors with fonts loading.

        See spyder-ide/qtawesome#167 and spyder-ide/spyder#18642 for
        context.
        """
        fonts_directory = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'fonts')
        if os.name == 'nt':
            fonts_directory = self._install_fonts(fonts_directory)
        return fonts_directory

    def _install_fonts(self, fonts_directory):
        """
        Copy the fonts to the user Fonts folder.
        
        Based on https://stackoverflow.com/a/41841088/15954282
        """
        # Try to get LOCALAPPDATA path
        local_appdata_dir = os.environ.get('LOCALAPPDATA', None)
        if not local_appdata_dir:
            return fonts_directory

        # Construct path to fonts from LOCALAPPDATA
        user_fonts_dir = os.path.join(
            local_appdata_dir, 'Microsoft', 'Windows', 'Fonts')
        os.makedirs(user_fonts_dir, exist_ok=True)

        # Setup bundled fonts on the LOCALAPPDATA fonts directory
        for root, __, files in os.walk(fonts_directory):
            for filename in files:
                src_path = os.path.join(root, filename)
                dst_filename = filename
                dst_path = os.path.join(
                    user_fonts_dir,
                    dst_filename
                )

                # Check if font already exists and proceed with copy font
                # process if needed or skip it
                if os.path.isfile(dst_path):
                    continue
                shutil.copy(src_path, dst_path)

                # Further process the font file (`.ttf`)
                if os.path.splitext(filename)[-1] == '.ttf':
                    # Load the font in the current session
                    if not gdi32.AddFontResourceW(dst_path):
                        try:
                            os.remove(dst_path)
                        except OSError:
                            # Possible permission error when trying to remove
                            # a font which potentially is already in use
                            # See spyder-ide/qtawesome#236
                            continue

                    # Store the fontname/filename in the registry
                    fontname = os.path.splitext(filename)[0]

                    # Try to get the font's real name
                    cb = wintypes.DWORD()
                    if gdi32.GetFontResourceInfoW(
                            filename, ctypes.byref(cb), None, GFRI_DESCRIPTION):
                        buf = (ctypes.c_wchar * cb.value)()
                        if gdi32.GetFontResourceInfoW(
                                filename, ctypes.byref(cb), buf, GFRI_DESCRIPTION):
                            fontname = buf.value
                    is_truetype = wintypes.BOOL()
                    cb.value = ctypes.sizeof(is_truetype)
                    gdi32.GetFontResourceInfoW(
                        filename, ctypes.byref(cb), ctypes.byref(is_truetype),
                        GFRI_ISTRUETYPE)
                    if is_truetype:
                        fontname += ' (TrueType)'
                    try:
                        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, FONTS_REG_PATH, 0,
                                            winreg.KEY_SET_VALUE) as key:
                            winreg.SetValueEx(key, fontname, 0, winreg.REG_SZ, filename)
                    except OSError:
                        # Needed to support older Windows version where
                        # font installation per user is not possible/related registry
                        # entry is not available
                        # See spyder-ide/qtawesome#214 
                        return fonts_directory

        return user_fonts_dir
