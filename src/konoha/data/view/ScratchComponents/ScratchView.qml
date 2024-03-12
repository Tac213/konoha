import QtQuick

Flickable {
    id: root
    clip: true
    contentWidth: scene.width
    contentHeight: scene.height
    contentX: 0
    contentY: 0

    ScratchScene {
        id: scene
    }

    ScratchHandler {
        id: handler
        scene: scene
        view: root
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
                event.accepted = true;
                console.log("Right Click");
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
}
