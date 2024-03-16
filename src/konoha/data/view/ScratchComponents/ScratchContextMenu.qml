import QtQuick
import QtQuick.Controls
import Python.ASTVMHelper  // qmllint disable import
import "../script/component-creation.js" as ComponentCreation

Menu {
    id: root
    property var astvmActions: new Map()
    property var astvmCategoryInfo: undefined
    required property var handler
    // qmllint disable import type
    ASTVMHelper {
        id: astvmHelper
    }
    // qmllint enable import type
    TextField {
        id: searchInput
        placeholderText: qsTr("Search...")
        focus: true
        onTextEdited: () => {
            root.build(this.text);
        }
    }
    Component.onCompleted: () => {
        this.createASTVMActions();
        this.astvmCategoryInfo = astvmHelper.get_astvm_category_info();
    }

    function createASTVMActions() {
        for (const astvmClassName of astvmHelper.get_all_astvm_class_names()) {
            const astvmShowName = astvmHelper.get_astvm_class_show_name(astvmClassName);
            new ComponentCreation.ComponentCreation(qmlEngine.get_file_url("view/ScratchComponents/ASTVMAction.qml"), this, {
                "astvmClassName": astvmClassName,
                "text": astvmShowName
            }, action => {
                this.astvmActions[action.astvmClassName] = action;
                action.triggered.connect(
                // this.handler.createNode(action.astvmClassName, (this.parent.contentX + this.x) / this.handler.scene.currentZoom, (this.parent.contentY + this.y) / this.handler.scene.currentZoom);
                () => {});
            });
        }
    }

    function buildAndPopup() {
        searchInput.text = "";
        this.build();
        this.popup();
    }

    function build(filterText = "") {
        this.clear();
        const buildFunction = (data, parentMenu) => {
            for (const [itemName, item] of Object.entries(data)) {
                if (typeof item === "boolean") {
                    parentMenu.addAction(this.astvmActions[itemName]);
                } else if (typeof item === "object") {
                    new ComponentCreation.ComponentCreation(qmlEngine.get_file_url("view/ScratchComponents/ScratchSubContextMenu.qml"), parentMenu, {
                        "title": itemName
                    }, menu => {
                        parentMenu.addMenu(menu);
                        buildFunction(item, menu);
                    });
                }
            }
        };
        if (filterText) {
            let allActions = {};
            const filterItems = data => {
                let res = {};
                for (const [itemName, item] of Object.entries(data)) {
                    if (typeof item === "boolean") {
                        if (this._filterAction(filterText, itemName)) {
                            res[itemName] = item;
                            allActions[itemName] = item;
                        }
                    } else if (typeof item === "object") {
                        const childRes = filterItems(item);
                        if (Object.keys(childRes).length) {
                            res[itemName] = childRes;
                        }
                    }
                }
                return res;
            };
            let filteredItems = filterItems(this.astvmCategoryInfo);
            if (Object.keys(allActions).length <= 10) {
                filteredItems = allActions;
            }
            buildFunction(filteredItems, this);
        } else {
            buildFunction(this.astvmCategoryInfo, this);
        }
    }

    function clear() {
        while (true) {
            if (this.actionAt(1)) {
                this.takeAction(1);
            } else if (this.itemAt(1)) {
                this.takeItem(1);
            } else if (this.menuAt(1)) {
                this.takeMenu(1);
            } else {
                break;
            }
        }
    }

    function _filterAction(filterText, actionName) {
        const lowerFilterText = filterText.toLowerCase();
        const lowerActionName = actionName.toLowerCase();
        return lowerActionName.includes(lowerFilterText);
    }
}
