from PySide6.QtCore import QObject, Slot, Property
from PySide6.QtGui import QFont
from PySide6.QtQml import QmlElement

import qtawesome as qta

QML_IMPORT_NAME = "Gui.RegisterElement"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class QtAwesomIconFont(QObject):
    def __init__(self):
        super().__init__()
        self._iconic_font = qta._instance()

    @Property(dict, constant=True)
    def fontMaps(self):
        return self._iconic_font.charmap

    @Slot(str, int, result=QFont)
    def font(self, prefix, size):
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
        return self._iconic_font.font(prefix, size)

    @Slot(str, result=str)
    def charmap(self, prefixed_name):
        """
        Return the character map used for a given font.

        Returns
        -------
        return_value: dict
            The dictionary mapping the icon names to the corresponding unicode character.

        """
        prefix, name = prefixed_name.split('.')
        return self._iconic_font.charmap[prefix][name]
