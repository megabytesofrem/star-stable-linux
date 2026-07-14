#!/bin/bash

cat << 'EOF'
            .''           Star Stable Linux Launcher
  ._.-.___.' (`\          @megabytesofrem
 //(        ( `'
'/ )\ ).__. ) 
' <' `\ ._/'\
   `   \     \
-----------------------------------------------------
EOF

# Export this so every sub-process (wine, winetricks) inherits it
export WINEPREFIX="$HOME/.wine_starstable"
export WINEARCH="win64" # Enforces clean 64-bit prefix generation

# Force Wine to ignore specific Windows process security attributes
# that Chromium uses to lock down its sandbox.
export WINEESYNC=1
export WINEFSYNC=1
export WINEDEBUG=-all  # Keep the logs clean while we test

export WINE64_ALLOW_MITIGATION_POLICY=1

star_stable_installed() { [ -d "$WINEPREFIX" ] && return 0 || return 1; }

if ! command -v curl &> /dev/null; then
    echo "Error: curl is not installed"
    exit 1
fi

if ! command -v wine &> /dev/null; then
    echo "Error: wine is not installed"
    exit 1
fi

install() {
    # Initialize a new Wine prefix for Star Stable
    mkdir -p "$WINEPREFIX"
    
    echo "Installer: Initializing Wine prefix..."
    wineboot --init

    echo "Installer: Downloading installer..."
    curl -L -o "$WINEPREFIX/drive_c/starstable_installer.exe" "https://launcher-release-prod.starstable.com/latest/Star%20Stable%20Online%20Setup.exe"

    echo "Installer: Installing windows prerequisites..."
    winetricks -q corefonts vcrun2019 dxvk

    echo "Installer: Launching installer..."
    cd "$WINEPREFIX/drive_c" || exit 1
    wine starstable_installer.exe
}

uninstall() {
    if [ -d "$WINEPREFIX" ]; then
        echo "Installer: Uninstalling Star Stable..."
        rm -rf "$WINEPREFIX"
        echo "Installer: Star Stable has been uninstalled."
    else
        echo "Installer: Star Stable is not installed."
    fi
}


launch() {
    echo "Installer: Launching Star Stable..."
    wine "$WINEPREFIX/drive_c/Program Files/Star Stable Online/Star Stable Online.exe"
}

case "$1" in
  install)
    install
    ;;
  uninstall)
    uninstall
    ;;
  launch)
    launch
    ;;
  *)
    echo "Usage: $0 {install|uninstall|launch}"
    exit 1
    ;;
esac