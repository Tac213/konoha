import QtQuick
import QtQuick.Controls

TextField {
    id: root
    required property int index
    required property string argName
    required property string inputType
    Component {
        id: intValidator
        IntValidator {
        }
    }
    Component {
        id: doubleValidator
        DoubleValidator {
        }
    }
    Component {
        id: variableValidator
        RegularExpressionValidator {
            regularExpression: /[a-zA-Z_]+[0-9a-zA-Z_]*/
        }
    }
    Loader {
        id: validatorLoader
        sourceComponent: {
            if (root.inputType === "int") {
                return intValidator;
            } else if (root.inputType == "float") {
                return doubleValidator;
            } else if (root.inputType == "variable") {
                return variableValidator;
            }
            return undefined;
        }
    }
    validator: validatorLoader.item
    onTextEdited: newText => {
        this.getNode().updateModelArgValue(this.argName, this.getValue());
    }

    function getNode() {
        return this.parent;
    }

    function setValue(value) {
        this.text = "" + value;
    }

    function getValue() {
        if (this.inputType === "int" || this.inputType === "float") {
            return Number(this.text);
        }
        return this.text;
    }
}
