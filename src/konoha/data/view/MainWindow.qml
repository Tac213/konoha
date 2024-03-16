import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "ScratchComponents" as ScratchComponents
import Python.FileUrlHelper  // qmllint disable import
import Python.FileEditor  // qmllint disable import
import Python.Reloader  // qmllint disable import

ApplicationWindow {
    id: root

    title: qsTr("konoha")
    width: 800
    height: 600
    visible: true

    menuBar: MenuBar {
        Menu {
            title: qsTr("&File")
            MenuItem {
                text: qsTr("&Open")
                onTriggered: () => {
                    openFileDialog.open();
                }
            }
            MenuItem {
                text: qsTr("&Save")
                onTriggered: () => {
                    console.log("Save File");
                }
            }
            MenuItem {
                text: qsTr("&Save As")
                onTriggered: () => {
                    saveFileDialog.open();
                }
            }
            MenuItem {
                text: qsTr("&Exit")
                onTriggered: () => {
                    Qt.quit();
                }
            }
        }
        Menu {
            title: qsTr("&Developer")
            MenuItem {
                text: qsTr("&Toggle Console")
                onTriggered: () => {
                    root.toggleConsoleWindow();
                }
            }
            MenuItem {
                text: qsTr("&Reload Qml")
                onTriggered: () => {
                    qmlEngine.reload();
                    root.close();
                }
            }
            MenuItem {
                text: qsTr("&Reload konoha")
                onTriggered: () => {
                    packageReloader.reload();
                }
            }
        }
    }
    RowLayout {
        anchors.fill: parent
        ScratchComponents.ScratchView {
            id: scratchView
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }

    Item {
        focus: true
        Keys.onPressed: event => {
            if (event.key === Qt.Key_QuoteLeft) {
                root.toggleConsoleWindow();
            } else if (event.key === Qt.Key_F5) {
                qmlEngine.reload();
                root.close();
            }
        }
    }

    OutputWindow {
        id: consoleWindow
    }

    function toggleConsoleWindow() {
        consoleWindow.visible = !consoleWindow.visible;
    }
    FileUrlHelper {
        id: fileUrlHelper
    }
    FileEditor {
        id: fileEditor
    }
    PackageReloader {
        id: packageReloader
    }

    FileDialog {
        id: openFileDialog
        title: qsTr("Open Python File")
        fileMode: FileDialog.OpenFile
        nameFilters: ["Python files (*.py)"]
        currentFolder: fileUrlHelper.root_dir
        onAccepted: () => {
            const fileURL = this.selectedFile.toString();
            const astvm = fileEditor.open_file(fileURL);
            scratchView.loadASTVM(astvm);
        }
    }

    FileDialog {
        id: saveFileDialog
        title: qsTr("Save Python File As")
        fileMode: FileDialog.SaveFile
        nameFilters: ["Python files (*.py)"]
        currentFolder: fileUrlHelper.root_dir
        onAccepted: () => {
            const fileURL = this.selectedFile.toString();
            fileEditor.save_file(fileURL, scratchView.getASTVM());
        }
    }
}
