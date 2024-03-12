import QtQuick
import "../script/component-creation.js" as ComponentCreation

Item {
    id: scene
    objectName: 'konohaScene'
    width: 1600
    height: 1600
    transform: Scale {
        id: sceneScaler
        origin.x: 0
        origin.y: 0
    }
    property real currentZoom: 1.0
    property real minZoom: 0.2
    property real maxZoom: 2.0
    property real zoomStride: 0.1
    property var scaler: sceneScaler
    property var nodes: new Map()

    Canvas {
        id: grid
        anchors.fill: parent
        property int wgrid: 60
        onPaint: {
            const ctx = getContext('2d');
            ctx.lineWidth = 1;
            ctx.strokeStyle = 'black';
            ctx.beginPath();
            const nrows = height / this.wgrid;
            for (var i = 0; i < nrows + 1; i++) {
                ctx.moveTo(0, this.wgrid * i);
                ctx.lineTo(width, this.wgrid * i);
            }
            const ncols = width / this.wgrid;
            for (var j = 0; j < ncols + 1; j++) {
                ctx.moveTo(this.wgrid * j, 0);
                ctx.lineTo(this.wgrid * j, height);
            }
            ctx.closePath();
            ctx.stroke();
        }
    }

    function createNode(nodeModel, posX, posY, onCreated) {
        new ComponentCreation.ComponentCreation('qrc:/konoha/view/ScratchComponents/Items/Node.qml', this, {
            "model": nodeModel,
            "x": posX,
            "y": posY
        }, node => {
            onCreated(node);
        });
    }

    function getView() {
        return this.parent.parent;
    }

    function getHandler() {
        return this.parent.parent.getHandler();
    }
}
