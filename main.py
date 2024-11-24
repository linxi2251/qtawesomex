# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtCore import QSortFilterProxyModel, Qt
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine, QmlElement

from qta_icon_font import QtAwesomIconFont  # noqa

QML_IMPORT_NAME = "Gui.RegisterElement"
QML_IMPORT_MAJOR_VERSION = 1
from rc_resources import *  # noqa


@QmlElement
class CustomProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)  # 不区分大小写过滤


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    app.setApplicationName("QtAwesomeIconFont")
    app.setOrganizationName("QtAwesomeIconFont")
    app.setOrganizationDomain("QtAwesomeIconFont.com")
    app.setWindowIcon(QIcon(":/favicon.ico"))
    engine = QQmlApplicationEngine()
    app.aboutToQuit.connect(engine.deleteLater)
    # engine.addImportPath(sys.path[0])
    engine.addImportPath("qrc:/")
    engine.loadFromModule("Gui", "Main")
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
