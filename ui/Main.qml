import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts

ApplicationWindow {
    visible: true
    width: 520
    height: 360
    title: "Star Stable Linux Launcher"

    Connections {
        target: backend

        function onShowUninstallDialog() {
            uninstallConfirm.open()
        }
    }

    // -- Dialogs --

    MessageDialog {
        id: installFinished
        buttons: MessageDialog.Ok
        title: "Installation Complete"
        text: "Star Stable has been installed successfully!"
    }

    Dialog {
        id: uninstallConfirm
        title: "Confirm Uninstall"
        modal: true
        anchors.centerIn: parent       
        width: 450 

        standardButtons: Dialog.Yes | Dialog.No

        // Custom layout for the icon and centered text
        contentItem: RowLayout {
            spacing: 20
            width: parent.width

            // Information Icon (Uses standard Qt standard icon provider)
            Image {
                id: infoIcon
                source: "image://theme/dialog-information"
                sourceSize.width: 48
                sourceSize.height: 48
                Layout.alignment: Qt.AlignVCenter
            }

            // Centered Confirmation Text
            Text {
                text: "Are you sure you want to uninstall Star Stable?"
                font.pixelSize: 14
                color: "white"
                wrapMode: Text.Wrap
                Layout.fillWidth: true
                
                // Centers text within its allotted space
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }

        onAccepted: {
            backend.start_script("uninstall")
        }
        
        onRejected: {
            uninstallConfirm.close()
        }
    }

    // -- UI --

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 12

            Image {
                source: "../resources/star_stable_logo.png"
                fillMode: Image.PreserveAspectFit
                width: 200
                height: 200
                Layout.preferredWidth: 200
                Layout.preferredHeight: 200
                Layout.alignment: Qt.AlignHCenter
            }
            Label {
                text: "Unofficial Star Stable Online Launcher for Linux"
                horizontalAlignment: Text.AlignHCenter
                Layout.fillWidth: true
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Button {
                id: installButton
                enabled: !backend.is_busy

                onClicked: backend.install_uninstall_star_stable()
                Layout.fillWidth: true

                background: Rectangle {
                    implicitWidth: 100
                    implicitHeight: 40
                    radius: 12
                    color: !installButton.pressed ? "#ffffff" : "#d4d4d4"

                    border.color: "#fc03b1"
                    border.width: 2
                }

                contentItem: Text {
                    text: backend.is_installed ? "Uninstall Star Stable" : "Install Star Stable"
                    color: "black"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                opacity: enabled ? 1.0 : 0.5
            }

            Button {
                id: launchButton

                enabled: backend.is_installed && !backend.is_busy

                onClicked: backend.launch_star_stable()
                Layout.fillWidth: true

                background: Rectangle {
                    implicitWidth: 100
                    implicitHeight: 40
                    radius: 12
                    color: !launchButton.enabled ? "#fc03b1" : (launchButton.pressed ? "#c40088" : "#e602a0")
                }

                contentItem: Text {
                    text: "Launch Star Stable"
                    color: launchButton.enabled ? "white" : (launchButton.pressed ? "white" : "black")
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                opacity: enabled ? 1.0 : 0.5
            }
        }

        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 8

            Label {
                text: backend.status
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: 13
            }

            Spinner {
                id: statusSpinner
                isLoading: backend.is_busy
                
                Layout.preferredWidth: 24
                Layout.preferredHeight: 24
                Layout.alignment: Qt.AlignVCenter
            }
        }
    }
}