import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Fusion as CF
import Gui.RegisterElement
import QtQuick.Window
import QtCore as QC

CF.ApplicationWindow {
    id: root
    width: 743
    height: 480
    visible: true
    title: qsTr("QtAwsome图标浏览器")
    readonly property string aLL_COLLECTIONS: "All"

    palette.window: theme.currentIndex === 0 ? "#333" : "#fff"
    palette.windowText: theme.currentIndex === 0 ? "#fff" : "#333"
    palette.base: theme.currentIndex === 0 ? "#222" : "#f5f5f5"
    palette.text: theme.currentIndex === 0 ? "#fff" : "#333"
    palette.button: theme.currentIndex === 0 ? "#555" : "#ddd"
    palette.buttonText: theme.currentIndex === 0 ? "#fff" : "#333"
    // 创建代理模型
    CustomProxyModel {
        id: _proxyModel
        sourceModel: _iconNamesModel
    }
    ListModel {
        id: _iconNamesModel
    }

    QC.Settings {
        id: settings
        property alias theme: theme.currentIndex
    }

    component IconFont: CF.Label {
        id: iconLbRoot
        property string name
        property int iconSize: 16
        onNameChanged: {
            iconLbRoot.font = iconfont.font(name.split(".")[0], iconSize)
            iconLbRoot.text = iconfont.charmap(name)
        }
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
    function updateFilter() {
        let reString = ""
        const group = _comboFont.currentText
        if (group !== root.aLL_COLLECTIONS) {
            reString += `^${group}\\.` // 注意：这里的\转义
        }
        const searchTerm = _lineEditFilter.text
        if (searchTerm) {
            reString += `.*${searchTerm}.*$`
        }
        try {
            _proxyModel.setFilterRegularExpression(reString)
        } catch (error) {
            console.log(error)
        }
    }

    QtAwesomIconFont {
        id: iconfont

        Component.onCompleted: {
            for (let fontCollection in iconfont.fontMaps) {
                const fontData = iconfont.fontMaps[fontCollection]
                for (let iconName in fontData) {
                    _iconNamesModel.append({
                                               "display": `${fontCollection}.${iconName}`
                                           })
                }
            }
        }
    }
    Column {
        id: col
        anchors.fill: parent
        anchors.margins: 5
        RowLayout {
            id: topArea
            width: parent.width
            height: 50
            CF.ComboBox {
                Layout.preferredWidth: 60
                id: _comboFont
                model: [root.aLL_COLLECTIONS].concat(Object.keys(
                                                         iconfont.fontMaps))
                currentIndex: 0
                onCurrentTextChanged: {
                    grid.focus = true
                    Qt.callLater(updateFilter)
                }
            }
            CF.TextField {
                id: _lineEditFilter
                Layout.fillWidth: true
                placeholderText: "Search"

                onTextChanged: {
                    Qt.callLater(updateFilter)
                }
                IconFont {
                    id: clearBtn
                    anchors.right: parent.right
                    anchors.rightMargin: 5
                    name: "ri.close-circle-fill"
                    height: parent.height
                    iconSize: 16
                    visible: _lineEditFilter.text !== ""
                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            _lineEditFilter.text = ""
                        }
                    }
                }
            }
            CF.TextField {
                id: _currentSelectedIconName
                readOnly: true
                Layout.preferredWidth: 150
                text: _proxyModel.data(_proxyModel.index(grid.currentIndex, 0),
                                       0) ? _proxyModel.data(
                                                _proxyModel.index(
                                                    grid.currentIndex,
                                                    0), 0) : ""
                horizontalAlignment: Text.AlignHCenter
            }
            CF.Button {
                text: "复制图标"
                onClicked: {
                    _currentSelectedIconName.selectAll()
                    _currentSelectedIconName.copy()
                    grid.focus = true
                }
            }

            CF.ComboBox {
                id: theme
                model: ["暗色", "亮色"]
                currentIndex: 0
                Layout.preferredWidth: 60
            }
        }
        Component {
            id: iconsDelegate
            Item {
                required property int index
                required property string display
                width: grid.cellWidth
                height: grid.cellHeight
                Column {
                    anchors.centerIn: parent
                    IconFont {
                        name: display
                        iconSize: 48
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                    CF.Label {
                        id: iconLb
                        text: display
                        elide: Text.ElideRight
                        width: grid.cellWidth
                        horizontalAlignment: Text.AlignHCenter
                    }
                }
                MouseArea {
                    anchors.fill: parent
                    propagateComposedEvents: true
                    onClicked: {
                        grid.currentIndex = index
                        grid.focus = true
                    }
                }
            }
        }
        Component {
            id: highlight
            Rectangle {
                width: grid.cellWidth
                height: grid.cellHeight
                color: palette.highlight
                radius: 5
                opacity: 0.5
            }
        }
        GridView {
            id: grid
            width: parent.width
            height: parent.height - topArea.height
            model: _proxyModel
            cellWidth: 80
            cellHeight: 80
            clip: true
            focus: true
            highlight: highlight
            delegate: iconsDelegate
            CF.ScrollBar.vertical: CF.ScrollBar {
                contentItem: Rectangle {
                    implicitWidth: 6
                    implicitHeight: 6
                    radius: 3
                    color: "gray"
                }
            }
        }
    }
}
