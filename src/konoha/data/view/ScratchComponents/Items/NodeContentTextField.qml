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
    Loader {
        id: validatorLoader
        sourceComponent: {
            if (root.inputType === "int") {
                return intValidator;
            } else if (root.inputType == "float") {
                return doubleValidator;
            }
            return undefined;
        }
    }
    validator: validatorLoader.item

    function setValue(value) {
        this.text = "" + value;
    }

    function getValue(value) {
        if (this.inputType === "int" || this.inputType === "float") {
            return Number(this.text);
        }
        return this.text;
    }
}
