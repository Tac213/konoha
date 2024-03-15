import QtQuick
import "." as ScratchItems
import "../../script/component-creation.js" as ComponentCreation

Item {
    id: root
    width: this.minimumWidth
    height: this.minimumHeight
    required property var model
    property real wingWidth: 20
    property real contentXMargin: 15
    property real contentYMargin: 20
    property var blockInfos: []  // {contentWidth, contentHeight, blockHeight}
    property var blockContents: []  // {index, contentTexts, contentArgs, snapIndicator}
    property var contentTexts: []
    property var contentArgs: []
    property real minimumWidth: 200
    property real minimumHeight: 100
    property real minimumBlockHeight: 40
    property bool snapped: false
    property var nextNode: undefined
    property var blockNextNode: new Map()

    Drag.active: mouseArea.drag.active
    Drag.hotSpot.x: this.wingWidth
    Drag.hotSpot.y: 0
    Drag.keys: [model.is_statement ? 'konohaStatement' : 'konohaExpression']

    Component {
        id: wing
        Rectangle {
            // id: wing
            // width: root.wingWidth
            // height: root.height
            color: 'LightCoral'
        }
    }
    Component {
        id: statementSnapIndicator
        DropArea {
            property bool isBlock: false
            x: 0
            height: 40
            keys: ['konohaStatement']
            onDropped: drop => {
                if (this.getNode().nextNode) {
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
                const loader = this.parent;
                return loader.parent;
            }
        }
    }
    Component {
        id: statementBody
        ScratchItems.StatementNodeShape {
            // id: body
            // x: root.wingWidth
            y: 0
            // width: root.width - root.wingWidth
            // height: root.height
            fillColor: 'LightSlateGray'
        }
    }
    Component {
        id: codeBlockBody
        ScratchItems.CodeBlockNodeShape {
            // id: body
            // x: root.wingWidth
            y: 0
            // width: root.width - root.wingWidth
            // height: root.height
            fillColor: 'LightSlateGray'
        }
    }
    Component {
        id: expressionBody
        ScratchItems.ExpressionNodeShape {
            // id: body
            // x: root.wingWidth
            y: 0
            // width: root.width - root.wingWidth
            // height: root.height
            fillColor: 'LightSlateGray'
        }
    }
    Loader {
        id: wingLoader
        sourceComponent: root.model.is_statement ? wing : undefined
        onLoaded: () => {
            wingWidthBinder.target = this.item;
            wingHeightBinder.target = this.item;
        }
    }
    Loader {
        id: snapIndicatorLoader
        sourceComponent: root.model.is_statement ? statementSnapIndicator : undefined
        onLoaded: () => {
            snapIndicatorWidthBinder.target = this.item;
            snapIndicatorYBinder.target = this.item;
        }
    }
    Loader {
        id: bodyLoader
        sourceComponent: root.model.is_statement ? (root.model.is_code_block ? codeBlockBody : statementBody) : expressionBody
        onLoaded: () => {
            bodyXBinder.target = this.item;
            bodyWidthBinder.target = this.item;
            if (root.model.is_code_block) {
                bodyBlockInfosBinder.target = this.item;
                this.item.heightBinder.target = root;
            } else {
                bodyHeightBinder.target = this.item;
            }
        }
    }
    Binding {
        id: wingWidthBinder
        property: 'width'
        value: root.wingWidth
    }
    Binding {
        id: wingHeightBinder
        property: 'height'
        value: root.height
    }
    Binding {
        id: snapIndicatorWidthBinder
        property: 'width'
        value: root.width
    }
    Binding {
        id: snapIndicatorYBinder
        property: 'y'
        value: root.height
    }
    Binding {
        id: bodyXBinder
        property: 'x'
        value: root.wingWidth
    }
    Binding {
        id: bodyWidthBinder
        property: 'width'
        value: root.width - root.wingWidth
    }
    Binding {
        id: bodyHeightBinder
        property: 'height'
        value: root.height
    }
    Binding {
        id: bodyBlockInfosBinder
        property: 'blockInfos'
        value: root.blockInfos
    }
    // TODO: Connect model signals
    ScratchItems.NodeContextMenu {
        id: contextMenu
        node: root
    }
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        drag.target: parent.snapped ? parent.getDragTarget() : parent
        preventStealing: true
        onReleased: event => {
            if (this.parent.Drag.target) {
                const action = this.parent.Drag.drop();
                if (action === Qt.MoveAction) {
                    if (this.parent.model.is_statement) {
                        const upperNode = this.parent.Drag.target.getNode();  // call getNode function on DropArea
                        const lowerNode = this.parent;
                        const isBlock = this.parent.Drag.target.isBlock;
                        const blockIndex = this.parent.Drag.target.index;
                        lowerNode.getHandler().snapStatement(upperNode, lowerNode, isBlock, blockIndex);
                    } else {
                        const contentArgElement = this.parent.Drag.target.parent;
                        const expressionNode = this.parent;
                        expressionNode.getHandler().snapExpression(expressionNode, contentArgElement);
                    }
                }
            }
        }
        onClicked: event => {
            if (event.button === Qt.RightButton) {
                contextMenu.popup();
                event.accepted = true;
            }
        }
    }

    Component.onCompleted: () => {
        this.createBlockContent();
        this.createContent();
    }

    function createContent() {
        const parseResult = this.parseNodeDescription();
        const textList = parseResult.textList;
        const argList = parseResult.argList;
        let total = 0;
        let current = 0;
        textList.forEach((text, idx) => {
            if (text) {
                new ComponentCreation.ComponentCreation('qrc:/konoha/view/ScratchComponents/Items/NodeContentText.qml', root, {
                    "index": idx,
                    "text": text
                }, textElement => {
                    this.contentTexts.push(textElement);
                    current++;
                    if (current >= total) {
                        this.layoutContents();
                    }
                });
                total++;
            }
            if (idx < argList.length) {
                const argName = argList[idx];
                const inputType = this.model.input_argument_type_map[argName];
                if (inputType) {
                    this._createInputArg(argName, idx, inputType, inputElement => {
                        this.contentArgs.push(inputElement);
                        current++;
                        if (current >= total) {
                            this.layoutContents();
                        }
                    });
                } else {
                    new ComponentCreation.ComponentCreation('qrc:/konoha/view/ScratchComponents/Items/NodeContentArgument.qml', root, {
                        "index": idx,
                        "argName": argName
                    }, argElement => {
                        this.contentArgs.push(argElement);
                        current++;
                        if (current >= total) {
                            this.layoutContents();
                        }
                    });
                }
                total++;
            }
        });
    }

    function createBlockContent() {
        let total = 0;
        let current = 0;
        this.model.node_block_descriptions.forEach((blockDescription, index) => {
            this.blockContents.push({
                "index": index,
                "contentTexts": [],
                "contentArgs": [],
                "snapIndicator": undefined
            });
            const parseResult = this.parseNodeDescription(blockDescription);
            const textList = parseResult.textList;
            const argList = parseResult.argList;
            textList.forEach((text, idx) => {
                if (text) {
                    new ComponentCreation.ComponentCreation('qrc:/konoha/view/ScratchComponents/Items/NodeContentText.qml', root, {
                        "index": idx,
                        "text": text
                    }, textElement => {
                        this.blockContents[index].contentTexts.push(textElement);
                        current++;
                        if (current >= total) {
                            this.layoutContents();
                        }
                    });
                    total++;
                }
                if (idx < argList.length) {
                    const argName = argList[idx];
                    const inputType = this.model.input_argument_type_map[argName];
                    if (inputType) {
                        this._createInputArg(argName, idx, inputType, inputElement => {
                            this.blockContents[index].contentArgs.push(inputElement);
                            current++;
                            if (current >= total) {
                                this.layoutContents();
                            }
                        });
                    } else {
                        new ComponentCreation.ComponentCreation('qrc:/konoha/view/ScratchComponents/Items/NodeContentArgument.qml', root, {
                            "index": idx,
                            "argName": argName
                        }, argElement => {
                            this.blockContents[index].contentArgs.push(argElement);
                            current++;
                            if (current >= total) {
                                this.layoutContents();
                            }
                        });
                    }
                    total++;
                }
            });
            new ComponentCreation.ComponentCreation('qrc:/konoha/view/ScratchComponents/Items/CodeBlockSnapIndicator.qml', root, {
                "index": index
            }, snapIndicator => {
                snapIndicator.z = this.z - 1;
                this.blockContents[index].snapIndicator = snapIndicator;
                current++;
                if (current >= total) {
                    this.layoutContents();
                }
            });
            total++;
        });
    }

    function parseNodeDescription(nodeDescription = undefined) {
        if (nodeDescription === undefined) {
            nodeDescription = this.model.node_description;
        }
        const inputArgsRE = /{{\s*[a-zA-Z_]+[0-9a-zA-Z_]*\s*}}/gm;
        const variableNameRE = /[a-zA-Z_]+[0-9a-zA-Z_]*/gm;
        const textList = nodeDescription.split(inputArgsRE);
        const argList = [];
        let match = inputArgsRE.exec(nodeDescription);
        while (match) {
            const inputArgSring = match[0];
            const variableName = variableNameRE.exec(inputArgSring)[0];
            argList.push(variableName);
            variableNameRE.lastIndex = 0;
            match = inputArgsRE.exec(nodeDescription);
        }
        return {
            "textList": textList,
            "argList": argList
        };
    }

    function _createInputArg(argName, index, inputType, onCreated) {
        new ComponentCreation.ComponentCreation('qrc:/konoha/view/ScratchComponents/Items/NodeContentTextField.qml', root, {
            "index": index,
            "argName": argName,
            "inputType": inputType
        }, textField => {
            onCreated?.call(undefined, textField);
        });
    }

    function layoutContents() {
        const allBlockHeight = this.layoutBlockContents();
        this.contentTexts.sort((a, b) => a.index - b.index);
        this.contentArgs.sort((a, b) => a.index - b.index);
        const handleResult = this._handleSingleContent(this.contentTexts, this.contentArgs);
        if (allBlockHeight === 0) {
            this.width = handleResult.width;
            this.height = handleResult.height;
        }
        let contentX = this.wingWidth + this.contentXMargin;
        for (const content of handleResult.contents) {
            content.x = contentX;
            content.y = allBlockHeight + handleResult.height / 2 - content.height / 2;
            contentX += content.width;
        }
        const nextNode = this.getNextNode();
        if (nextNode) {
            nextNode.y = this.height;
        }
    }

    function layoutBlockContents() {
        this.blockContents.sort((a, b) => a.index - b.index);
        const blockInfos = this.blockInfos.slice(0, this.blockContents.length);
        let width = 0;
        let height = 0;
        this.blockContents.forEach((blockContent, index) => {
            if (index >= blockInfos.length) {
                blockInfos.push({
                    "contentWidth": 0,
                    "contentHeight": 0,
                    "blockHeight": 0
                });
            }
            const blockInfo = blockInfos[index];
            blockContent.contentTexts.sort((a, b) => a.index - b.index);
            blockContent.contentArgs.sort((a, b) => a.index - b.index);
            const handleResult = this._handleSingleContent(blockContent.contentTexts, blockContent.contentArgs);
            blockInfo.contentWidth = handleResult.width - this.wingWidth;
            blockInfo.contentHeight = handleResult.height;
            width = Math.max(width, handleResult.width);
            let contentX = this.wingWidth + this.contentXMargin;
            for (const content of handleResult.contents) {
                content.x = contentX;
                content.y = height + handleResult.height / 2 - content.height / 2;
                contentX += content.width;
            }
            height += handleResult.height;
            const blockWidth = this.getBlockWidth();
            blockContent.snapIndicator.x = this.wingWidth + blockWidth;
            blockContent.snapIndicator.y = height;
            blockContent.snapIndicator.width = blockInfo.contentWidth - blockWidth;
            let blockHeight = this.minimumBlockHeight;
            let nextNode = this.getBlockNextNode(index);
            if (nextNode) {
                nextNode.y = height;
            }
            while (nextNode) {
                blockHeight += nextNode.height;
                nextNode = nextNode.getNextNode();
            }
            blockInfo.blockHeight = blockHeight;
            height += blockInfo.blockHeight;
        });
        this.width = width;
        this.blockInfos = blockInfos;
        return height;
    }

    function _handleSingleContent(contentTexts, contentArgs) {
        let textIndex = 0;
        let argIndex = 0;
        const contents = [];
        let width = 0;
        let height = this.minimumHeight - this.contentYMargin * 2;
        while (textIndex < contentTexts.length || argIndex < contentArgs.length) {
            const currentText = contentTexts[textIndex];
            const currentArg = contentArgs[argIndex];
            if (currentText) {
                if (currentArg) {
                    if (currentText.index <= currentArg.index) {
                        contents.push(currentText);
                        textIndex++;
                        width += currentText.width;
                        height = Math.max(height, currentText.height);
                    } else {
                        contents.push(currentArg);
                        argIndex++;
                        width += currentArg.width;
                        height = Math.max(height, currentArg.height);
                    }
                } else {
                    contents.push(currentText);
                    textIndex++;
                    width += currentText.width;
                    height = Math.max(height, currentText.height);
                }
            } else if (currentArg) {
                contents.push(currentArg);
                argIndex++;
                width += currentArg.width;
                height = Math.max(height, currentArg.height);
            }
        }
        const targetWidth = Math.max(this.wingWidth + width + this.contentXMargin * 2, this.minimumWidth);
        const targetHeight = height + this.contentYMargin * 2;
        return {
            "contents": contents,
            "width": targetWidth,
            "height": targetHeight
        };
    }

    function getBlockWidth() {
        if (!this.model.is_code_block) {
            return undefined;
        }
        return bodyLoader.item ? bodyLoader.item.blockWidth : 50;
    }

    function getBlockOffset() {
        if (!this.model.is_code_block) {
            return undefined;
        }
        return bodyLoader.item ? bodyLoader.item.blockOffset : 5;
    }

    function getScene() {
        let candidate = this.parent;
        while (candidate) {
            if (candidate.objectName === 'konohaScene') {
                return candidate;
            }
            candidate = candidate.parent;
        }
        return null;
    }

    function getHandler() {
        const scene = this.getScene();
        return scene ? scene.getHandler() : null;
    }

    function getDragTarget() {
        if (!this.snapped) {
            return this;
        }
        let candidate = this.getSnappingNode();
        while (candidate) {
            if (!candidate.snapped) {
                return candidate;
            }
            candidate = candidate.getSnappingNode();
        }
        return null;
    }

    function getSnappingNode() {
        if (!this.snapped) {
            return undefined;
        }
        if (this.model.is_statement) {
            return this.parent;
        }
        return this.parent.parent;
    }

    function getNextNode() {
        return this.nextNode;
    }

    function getBlockNextNode(index) {
        return this.blockNextNode.get(index);
    }
}
