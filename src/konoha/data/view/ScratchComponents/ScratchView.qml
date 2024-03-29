import QtQuick
import Python.ASTEditor

Flickable {
    id: root
    clip: true
    contentWidth: scene.width
    contentHeight: scene.height
    contentX: 0
    contentY: 0

    ASTEditor {
        id: astEditor
    }

    ScratchScene {
        id: scene
    }

    ScratchHandler {
        id: handler
        scene: scene
        view: root
        astEditor: astEditor
    }

    ScratchContextMenu {
        id: scratchContextMenu
        handler: handler
    }

    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.RightButton
        onWheel: event => {
            root.zoom(event.angleDelta.y > 0, event.x, event.y);
            event.accepted = true;
        }
        onClicked: event => {
            if (event.button === Qt.RightButton) {
                scratchContextMenu.buildAndPopup();
                event.accepted = true;
            }
        }
    }

    function zoom(bigger, posX, posY) {
        let targetZoom = scene.currentZoom;
        if (bigger) {
            targetZoom += scene.zoomStride;
        } else {
            targetZoom -= scene.zoomStride;
        }
        targetZoom = Math.min(Math.max(targetZoom, scene.minZoom), scene.maxZoom);
        scene.currentZoom = targetZoom;
        scene.scaler.xScale = targetZoom;
        scene.scaler.yScale = targetZoom;
        this.resizeContent(scene.width * scene.currentZoom, scene.height * scene.currentZoom, Qt.point(posX, posY));
        this.returnToBounds();
    }

    function loadASTVM(astvm) {
        handler.loadASTVM(astvm);
    }

    function getASTVM() {
        return handler.astvm;
    }

    function getHandler() {
        return handler;
    }
}
