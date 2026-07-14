## 
##             .''           Star Stable Linux Launcher
##   ._.-.___.' (`\          @megabytesofrem
##  //(        ( `'
## '/ )\ ).__. ) 
## ' <' `\ ._/'\
##    `   \     \
## -----------------------------------------------------


import os
import sys
from pathlib import Path

from PyQt6.QtCore import (
    QObject,
    pyqtSignal,
    pyqtSlot,
    pyqtProperty,
    QProcess,
)
from PyQt6.QtWidgets import QApplication
from PyQt6.QtQml import QQmlApplicationEngine

class StarStableLinuxGUI(QObject):
    busyChanged = pyqtSignal()
    statusChanged = pyqtSignal()
    installedChanged = pyqtSignal()
    showUninstallDialog = pyqtSignal()
    showInstallFinish = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._status = "Waiting for an action"
        self._is_installed = False
        self._is_busy = False

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.on_output)
        self.process.readyReadStandardError.connect(self.on_output)
        self.process.finished.connect(self.on_finished)

        self.refresh_installed_status()

    # -- Signal Handlers --

    @pyqtProperty(bool, notify=busyChanged)
    def is_busy(self):
        return self._is_busy

    @pyqtProperty(bool, notify=installedChanged)
    def is_installed(self):
        return self._is_installed

    @pyqtProperty(str, notify=statusChanged)
    def status(self):
        return self._status

    def set_busy(self, value):
        self._is_busy = value
        self.busyChanged.emit()

    def set_status(self, value):
        self._status = value
        self.statusChanged.emit()

    def refresh_installed_status(self):
        self._is_installed = self.check_star_stable_installed()
        self.installedChanged.emit()

    def check_star_stable_installed(self):
        wineprefix = Path.home() / ".wine_starstable"
        return wineprefix.exists() and (wineprefix / "drive_c/Program Files/Star Stable Online/Star Stable Online.exe").exists()

    @pyqtSlot()
    def install_uninstall_star_stable(self):
        if self.check_star_stable_installed():
            # Show a confirmation dialog before uninstalling
            self.showUninstallDialog.emit()
        else:
            self.start_script("install")

    @pyqtSlot()
    def launch_star_stable(self):
        self.start_script("launch")


    # -- Process Management --

    def _start_script(self, command, start_detached=False):
        if self.process.state() != QProcess.ProcessState.NotRunning:
            return

        self.set_busy(True)
        self.set_status(f"Status: {command.capitalize()} started")

        if not start_detached:
            self.process.start("bash", ["./scripts/star-stable-linux.sh", command])
        else:
            self.process.startDetached("bash", ["./scripts/star-stable-linux.sh", command])

    @pyqtSlot(str)
    def start_script(self, command):
        if command == "launch":
            self._start_script(command, start_detached=True)
        else:
            self._start_script(command, start_detached=False)

    def on_output(self):
        data = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="ignore")
        for line in data.splitlines():
            if line.startswith("Installer:"):
                message = line[len("Installer:"):].strip()
                self.set_status(message)

    def on_finished(self):
        self.set_status("Status: Finished")
        self.set_busy(False)
        self.refresh_installed_status()

    @pyqtSlot()
    def killProcess(self):
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.kill()
            self.process.waitForFinished(3000)
            self.set_status("Status: Terminated")
            self.set_busy(False)

# -- Main UI code --

qml = """
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
                source: "resources/star_stable_logo.png"
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

        Label {
            text: backend.status
            horizontalAlignment: Text.AlignHCenter
            Layout.fillWidth: true
        }

        ProgressBar {
            indeterminate: backend.is_busy
            visible: true
            Layout.fillWidth: true
            Layout.preferredHeight: 24
        }
    }
}
"""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Breeze")  # Set the Breeze style for a consistent look

    engine = QQmlApplicationEngine()

    backend = StarStableLinuxGUI()
    app.aboutToQuit.connect(backend.killProcess)
    engine.rootContext().setContextProperty("backend", backend)

    engine.loadData(qml.encode("utf-8"))

    # Exit gracefully if QML loading fails
    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())