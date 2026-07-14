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
    QUrl,
    QProcess,

    pyqtSignal,
    pyqtSlot,
    pyqtProperty,
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Breeze")  # Set the Breeze style for a consistent look

    engine = QQmlApplicationEngine()

    backend = StarStableLinuxGUI()
    app.aboutToQuit.connect(backend.killProcess)
    engine.rootContext().setContextProperty("backend", backend)

    qml_path = Path(__file__).parent / "ui" / "Main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))

    # Exit gracefully if QML loading fails
    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())