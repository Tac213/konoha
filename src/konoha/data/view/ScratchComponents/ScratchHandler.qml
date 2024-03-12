import QtQml

QtObject {
    id: root
    required property var scene
    required property var view
    property var astvm: undefined

    function loadASTVM(astvm) {
        this.astvm = astvm;
        if (this.astvm.body.length === 0) {
            return;
        }
        let lastASTVM = this.astvm.body[0];
        for (const stmt of this.astvm.body) {
            this.createStatement(stmt, stmt === lastASTVM ? undefined : lastASTVM);
            lastASTVM = stmt;
        }
    }

    function createStatement(stmt, upperNode = undefined, isBlock = false, blockIndex = 0, posX = 100, posY = 100) {
        this.scene.createNode(stmt, posX, posY, node => {
            if (upperNode === undefined) {
                return;
            }
            this.snapStatement(upperNode, node, isBlock, blockIndex);
        });
    // TODO: create sub-stmt and sub-expr recursively
    }

    function createExpression(expr) {
    }

    function snapExpression(expressionNode, argElement) {
        if (expressionNode.model.is_statement) {
            return;
        }
        if (expressionNode.snapped) {
            return;
        }
        expressionNode.parent = argElement;
        expressionNode.x = -expressionNode.wingWidth;
        expressionNode.y = 0;
        expressionNode.snapped = true;
        argElement.width = expressionNode.width - expressionNode.wingWidth;
        argElement.height = expressionNode.height;
        argElement.enableSnap = false;
        argElement.snappingExpressionNode = expressionNode;
        let snappingNode = argElement.getNode();
        snappingNode.layoutContents();
        while (!snappingNode.model.is_statement && snappingNode.snapped) {
            const parentArgElement = snappingNode.parent;
            parentArgElement.width = snappingNode.width - snappingNode.wingWidth;
            parentArgElement.height = snappingNode.height;
            snappingNode = snappingNode.getSnappingNode();
            snappingNode.layoutContents();
        }
        while (snappingNode) {
            snappingNode.layoutContents();
            snappingNode = snappingNode.getSnappingNode();
        }
    // TODO: modify view model
    }

    function unsnapExpression(expressionNode) {
        if (expressionNode.model.is_statement) {
            return;
        }
        if (!expressionNode.snapped) {
            return;
        }
        const parentNode = expressionNode.getSnappingNode();
        const argElement = expressionNode.parent;
        const scenePos = this.scene.mapFromItem(expressionNode.parent, expressionNode.x, expressionNode.y);
        expressionNode.parent = this.scene;
        expressionNode.x = scenePos.x + 20;  // make some offset
        expressionNode.y = scenePos.y + 20;  // make some offset
        expressionNode.snapped = false;
        argElement.enableSnap = true;
        argElement.snappingExpressionNode = undefined;
    // TODO: modify view model
    }

    function snapStatement(upperNode, lowerNode, isBlock, blockIndex) {
        if (!upperNode.model.is_statement || !lowerNode.model.is_statement) {
            return;
        }
        if (lowerNode.snapped) {
            return;
        }
        lowerNode.parent = upperNode;
        if (!isBlock) {
            lowerNode.x = 0;
            lowerNode.y = upperNode.height;
            upperNode.nextNode = lowerNode;
            // TODO: Modify view model
        } else {
            const snapIndicator = upperNode.blockContents[blockIndex].snapIndicator;
            lowerNode.x = snapIndicator.x + upperNode.getBlockOffset();
            lowerNode.y = snapIndicator.y;
            snapIndicator.snappingNode = lowerNode;
            upperNode.blockNextNode.set(blockIndex, lowerNode);
            // TODO: Modify view model
            upperNode.layoutContents();
        }
        lowerNode.snapped = true;
        let snappingNode = upperNode.getSnappingNode();
        while (snappingNode) {
            snappingNode.layoutContents();
            snappingNode = snappingNode.getSnappingNode();
        }
    }

    function unsnapStatement(lowerNode) {
        if (!lowerNode.model.is_statement) {
            return;
        }
        if (!lowerNode.snapped) {
            return;
        }
        const upperNode = lowerNode.parent;
        this._unsnapStatement(upperNode, lowerNode);
    }

    function unsnapNextStatement(upperNode) {
        if (!upperNode.model.is_statement) {
            return;
        }
        const lowerNode = upperNode.getNextNode();
        if (!lowerNode) {
            return;
        }
        this._unsnapStatement(upperNode, lowerNode);
    }

    function _unsnapStatement(upperNode, lowerNode) {
        const scenePos = this.scene.mapFromItem(upperNode, lowerNode.x, lowerNode.y);
        lowerNode.parent = this.scene;
        lowerNode.x = scenePos.x + 20;  // make some offset
        lowerNode.y = scenePos.y + 20;  // make some offset
        lowerNode.snapped = false;
        if (upperNode.nextNode === lowerNode) {
            upperNode.nextNode = undefined;
            // TODO: Modify view model
        } else {
            let blockIndex;
            for (const [index, node] of upperNode.blockNextNode) {
                if (node === lowerNode) {
                    blockIndex = index;
                    break;
                }
            }
            if (blockIndex !== undefined) {
                upperNode.blockNextNode.delete(blockIndex);
                // TODO: Modify view model
            }
            // blockIndex may be different from blockContents, iterate for accurate snapIndicator
            let snapIndicator;
            for (const blockContent of upperNode.blockContents) {
                if (blockContent.snapIndicator.snappingNode === lowerNode) {
                    snapIndicator = blockContent.snapIndicator;
                    break;
                }
            }
            if (snapIndicator) {
                snapIndicator.snappingNode = undefined;
            }
        }
    }
}