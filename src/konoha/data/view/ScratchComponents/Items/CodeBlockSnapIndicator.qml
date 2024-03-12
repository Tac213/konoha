import QtQuick

DropArea {
    id: root
    required property int index
    property bool isBlock: true
    property var snappingNode: undefined
    x: 0
    height: 40
    keys: ['konohaStatement']
    onDropped: drop => {
        if (this.snappingNode) {
            return;
        }
        if (drop.source) {
            drop.accept();
        }
    }
    Rectangle {
        anchors.fill: parent
        color: 'Aquamarine'
        visible: parent.containsDrag
    }

    function getNode() {
        const node = this.parent;
        return node;
    }

    function isSnappingStatementNode() {
        return this.snappingNode !== undefined;
    }

    function getSnappingStatementNode() {
        return this.snappingNode;
    }
}
