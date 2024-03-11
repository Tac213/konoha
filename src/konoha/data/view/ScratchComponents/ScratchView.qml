import QtQuick

Flickable {
    id: root
    clip: true
    contentWidth: scene.width
    contentHeight: scene.height
    contentX: 0.5 * scene.width - 0.5 * this.width
    contentY: 0.5 * scene.height - 0.5 * this.height

    ScratchScene {
        id: scene
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
}