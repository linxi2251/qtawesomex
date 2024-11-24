/****************************************************************************
** Generated QML type registration code
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <QtQml/qqml.h>
#include <QtQml/qqmlmoduleregistration.h>

#if __has_include(<D:/Users/buf/Documents/A_workspace/QML_study/qtawesomex/main.py>)
#  include <D:/Users/buf/Documents/A_workspace/QML_study/qtawesomex/main.py>
#endif


#if !defined(QT_STATIC)
#define Q_QMLTYPE_EXPORT Q_DECL_EXPORT
#else
#define Q_QMLTYPE_EXPORT
#endif
Q_QMLTYPE_EXPORT void qml_register_types_Gui_RegisterElement()
{
    QT_WARNING_PUSH QT_WARNING_DISABLE_DEPRECATED
    qmlRegisterTypesAndRevisions<CustomProxyModel>("Gui.RegisterElement", 1);
    QMetaType::fromType<QAbstractItemModel *>().id();
    QMetaType::fromType<QAbstractItemModel::LayoutChangeHint>().id();
    QMetaType::fromType<QAbstractItemModel::CheckIndexOption>().id();
    QMetaType::fromType<QAbstractProxyModel *>().id();
    QMetaType::fromType<QSortFilterProxyModel *>().id();
    QT_WARNING_POP
    qmlRegisterModule("Gui.RegisterElement", 1, 0);
}

static const QQmlModuleRegistration guiRegisterElementRegistration("Gui.RegisterElement", qml_register_types_Gui_RegisterElement);
