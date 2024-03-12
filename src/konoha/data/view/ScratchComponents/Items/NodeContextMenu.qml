import QtQuick
import QtQuick.Controls

Menu {
    id: root
    required property var node

    Action {
        id: unsnapExpression
        text: qsTr('Unsnap this expression')
        enabled: !root.node.model.is_statement && root.node.snapped
        onTriggered: () => {
            root.node.getHandler().unsnapExpression(root.node);
        }
    }

    Action {
        id: unsnapPrevious
        text: qsTr('Unsnap previous statement')
        enabled: root.node.model.is_statement && root.node.snapped
        onTriggered: () => {
            root.node.getHandler().unsnapStatement(root.node);
        }
    }

    Action {
        id: unsnapNext
        text: qsTr('Unsnap next statement')
        enabled: root.node.model.is_statement && root.node.nextNode !== undefined
        onTriggered: () => {
            root.node.getHandler().unsnapNextStatement(root.node);
        }
    }
}
