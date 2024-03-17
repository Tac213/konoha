import QtQml

QtObject {
    id: root
    required property var scene
    required property var view
    required property var astEditor
    property var astvm: undefined

    function loadASTVM(astvm) {
        this.astvm = astvm;
        let index = 0;
        const onNodeCreated = node => {
            const stmt = this.astvm.body[++index];
            if (!stmt) {
                return;
            }
            this.createStatement(stmt, onNodeCreated, node);
        };
        const firstASTVM = this.astvm.body[index];
        if (!firstASTVM) {
            return;
        }
        this.createStatement(firstASTVM, onNodeCreated);
    }

    function createStatement(stmt, onCreated = undefined, upperNode = undefined, isBlock = false, blockIndex = 0, posX = 100, posY = 100) {
        this.scene.createNode(stmt, posX, posY, node => {
            const argElementMap = new Map();
            for (const argElement of node.contentArgs) {
                argElementMap.set(argElement.argName, argElement);
            }
            // create sub-expr recursively
            for (const argPropertyName of stmt.argument_property_names) {
                let arg;
                const inputType = stmt.input_argument_type_map[argPropertyName];
                const argElement = argElementMap.get(argPropertyName);
                if (inputType) {
                    if (inputType == "list_item") {
                        const [realArgName, argIndex] = argPropertyName.split(/_/);
                        arg = stmt[realArgName][Number(argIndex)];
                        this.createExpression(arg, undefined, argElement);
                    } else {
                        arg = stmt[argPropertyName];
                        argElement.setValue(arg);
                    }
                    continue;
                }
                arg = stmt[argPropertyName];
                this.createExpression(arg, undefined, argElement);
            }
            // create in-block sub-stmt recursively
            for (const [blockPropertyName, blockIndex] of stmt.code_block_map) {
                const blockASTVMs = stmt[blockPropertyName];
                let index = 0;
                const onBlockNodeCreated = blockNode => {
                    const stmt = this.astvm.body[++index];
                    if (!stmt) {
                        return;
                    }
                    this.createStatement(stmt, onBlockNodeCreated, blockNode);
                };
                const firstBlockASTVM = blockASTVMs[index];
                if (!firstBlockASTVM) {
                    continue;
                }
                this.createStatement(firstASTVM, onBlockNodeCreated, node, true, blockIndex);
            }
            // call onCreated
            onCreated?.call(undefined, node);
            // try to snap current node to the upper node
            if (upperNode === undefined) {
                return;
            }
            this.snapStatement(upperNode, node, isBlock, blockIndex, false);
        });
    }

    function createExpression(expr, onCreated = undefined, argElement = undefined, posX = 100, posY = 100) {
        this.scene.createNode(expr, posX, posY, node => {
            const argElementMap = new Map();
            for (const contentArgElement of node.contentArgs) {
                argElementMap.set(contentArgElement.argName, contentArgElement);
            }
            // create sub-expr recursively
            for (const argPropertyName of expr.argument_property_names) {
                let arg;
                const inputType = expr.input_argument_type_map[argPropertyName];
                const contentArgElement = argElementMap.get(argPropertyName);
                if (inputType) {
                    if (inputType == "list_item") {
                        const [realArgName, argIndex] = argPropertyName.split(/_/);
                        arg = expr[realArgName][Number(argIndex)];
                        this.createExpression(arg, undefined, contentArgElement);
                    } else {
                        arg = expr[argPropertyName];
                        contentArgElement.setValue(arg);
                    }
                    continue;
                }
                arg = expr[argPropertyName];
                this.createExpression(arg, undefined, contentArgElement);
            }
            // call onCreated
            onCreated?.call(undefined, node);
            // try to snap current node to the argument element
            if (argElement === undefined) {
                return;
            }
            this.snapExpression(node, argElement);
        });
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

    function snapStatement(upperNode, lowerNode, isBlock, blockIndex, modifyModel = true) {
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
            if (modifyModel) {
                if (this.astEditor.is_child(upperNode.model, this.astvm)) {
                    this.astEditor.insert_statement(this.astvm, upperNode.model, lowerNode.model);
                } else {
                    this.astEditor.top_insert_statement(this.astvm, lowerNode.model, upperNode.model);
                }
            }
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
