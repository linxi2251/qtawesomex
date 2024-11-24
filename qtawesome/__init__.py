import hashlib
import os

from PySide6.QtGui import QFontDatabase

# Local imports
from qtawesome.iconic_font import IconicFont, FontError
from qtawesome.iconic_font import SYSTEM_FONTS as _SYSTEM_FONTS

# Constants
_resource: dict[str, IconicFont] = {'iconic': None}

_BUNDLED_FONTS = (
    ('fa',
     'fontawesome4-webfont-4.7.ttf',
     'fontawesome4-webfont-charmap-4.7.json'),
    ('fa5',
     'fontawesome5-regular-webfont-5.15.4.ttf',
     'fontawesome5-regular-webfont-charmap-5.15.4.json'),
    ('fa5s',
     'fontawesome5-solid-webfont-5.15.4.ttf',
     'fontawesome5-solid-webfont-charmap-5.15.4.json'),
    ('fa5b',
     'fontawesome5-brands-webfont-5.15.4.ttf',
     'fontawesome5-brands-webfont-charmap-5.15.4.json'),
    ('ei',
     'elusiveicons-webfont-2.0.ttf',
     'elusiveicons-webfont-charmap-2.0.json'),
    ('mdi',
     'materialdesignicons5-webfont-5.9.55.ttf',
     'materialdesignicons5-webfont-charmap-5.9.55.json'),
    ('mdi6',
     'materialdesignicons6-webfont-6.9.96.ttf',
     'materialdesignicons6-webfont-charmap-6.9.96.json'),
    ('ph',
     'phosphor-1.3.0.ttf',
     'phosphor-charmap-1.3.0.json'),
    ('ri',
     'remixicon-2.5.0.ttf',
     'remixicon-charmap-2.5.0.json'),
    ('msc',
     'codicon-0.0.35.ttf',
     'codicon-charmap-0.0.35.json'),
)

# MD5 Hashes for font files bundled with qtawesome:
_MD5_HASHES = {
    'fontawesome4-webfont-4.7.ttf': 'b06871f281fee6b241d60582ae9369b9',
    'fontawesome5-regular-webfont-5.15.4.ttf': 'dc47e4089f5bcb25f241bdeb2de0fb58',
    'fontawesome5-solid-webfont-5.15.4.ttf': '5de19800fc9ae73438c2e5c61d041b48',
    'fontawesome5-brands-webfont-5.15.4.ttf': '513aa607d398efaccc559916c3431403',
    'elusiveicons-webfont-2.0.ttf': '207966b04c032d5b873fd595a211582e',
    'materialdesignicons5-webfont-5.9.55.ttf': 'b7d40e7ef80c1d4af6d94902af66e524',
    'materialdesignicons6-webfont-6.9.96.ttf': 'ecaabfbb23fdac4ddbaf897b97257a92',
    'phosphor-1.3.0.ttf': '5b8dc57388b2d86243566b996cc3a789',
    'remixicon-2.5.0.ttf': '888e61f04316f10bddfff7bee10c6dd0',
    'codicon-0.0.35.ttf': '8478f5b3df2158f7e4864473e34efda1',
}


def has_valid_font_ids(inst):
    """Validate instance's font ids are loaded to QFontDatabase.

    It is possible that QFontDatabase was reset or QApplication was recreated
    in both cases it is possible that font is not available.
    """
    # Check stored font ids are still available
    for font_id in inst.fontids.values():
        font_families = QFontDatabase.applicationFontFamilies(
            font_id
        )
        if not font_families:
            return False
    return True


def _instance():
    """
    Return the singleton instance of IconicFont.

    Functions ``icon``, ``load_font``, ``charmap``, ``font`` and
    ``set_defaults`` all rebind to methods of the singleton instance of IconicFont.
    """
    if (
            _resource['iconic'] is not None
            and not has_valid_font_ids(_resource['iconic'])
    ):
        # Reset cached instance
        _resource['iconic'] = None

    if _resource['iconic'] is None:
        # Verify that vendorized fonts are not corrupt
        if not _SYSTEM_FONTS:
            for fargs in _BUNDLED_FONTS:
                ttf_filename = fargs[1]
                ttf_hash = _MD5_HASHES.get(ttf_filename, None)
                if ttf_hash is None:
                    continue
                ttf_filepath = os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    "fonts", ttf_filename)
                with open(ttf_filepath, "rb") as f:
                    ttf_calculated_hash_code = hashlib.md5(f.read()).hexdigest()
                if ttf_calculated_hash_code != ttf_hash:
                    raise FontError(f"Font is corrupt at: '{ttf_filepath}'")

        _resource['iconic'] = IconicFont(*_BUNDLED_FONTS)
    return _resource['iconic']


def charmap(prefixed_name):
    """
    Return the character map used for a given font.

    Returns
    -------
    return_value: dict
        The dictionary mapping the icon names to the corresponding unicode character.

    """
    prefix, name = prefixed_name.split('.')
    return _instance().charmap[prefix][name]


def font(prefix, size):
    """
    Return the font corresponding to the specified prefix.

    This can be used to render text using the iconic font directly::

        import qtawesome as qta
        from qtpy import QtWidgets

        label = QtWidgets.QLabel(unichr(0xf19c) + ' ' + 'Label')
        label.setFont(qta.font('fa', 16))

    Parameters
    ----------
    prefix: str
        prefix string of the loaded font
    size: int
        size for the font

    """
    return _instance().font(prefix, size)
