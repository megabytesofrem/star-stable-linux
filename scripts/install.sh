#!/bin/bash

# Detect the target distro
detect_distro() {
    distro_id=$(cat /etc/os-release | grep -w ID | cut -d '=' -f 2 | tr -d '"')
    echo "$distro_id"
}

is_supported_distro() {
    distro_id=$(detect_distro)

    case "$distro_id" in
      ubuntu|debian|linuxmint|pop|elementary|zorin)
        ;;
      fedora|rhel|centos|rocky|almalinux)
        ;;
      opensuse|sles|sled)
        ;;
      arch|manjaro)
        ;;
      nixos)
        ;;
      *)
        echo "Error: Unsupported distro"
        exit 1
        ;;
    esac
}

default_install() {
    # Copy everything to /opt/star-stable-linux
    sudo cp -r . /opt/star-stable-linux

    # Create a .desktop file for the application
    sudo tee /usr/share/applications/star-stable-linux.desktop > /dev/null <<EOF
[Desktop Entry]
Name=Star Stable Linux
Comment=Star Stable Online Launcher for Linux
Exec=/opt/star-stable-linux/star-stable-linux-gui.py
Icon=/opt/star-stable-linux/ui/icon.png
Terminal=false
Type=Application
Categories=Game;
EOF
}

nixos_install() {
    # Copy everything to /opt/star-stable-linux
    sudo cp -r . /opt/star-stable-linux

    # Create a .desktop file for the application
    sudo tee /etc/xdg/autostart/star-stable-linux.desktop > /dev/null <<EOF
[Desktop Entry]
Name=Star Stable Linux
Comment=Star Stable Online Launcher for Linux
Exec=nix-shell /opt/star-stable-linux/shell.nix --run "sso-wine-env"
Icon=/opt/star-stable-linux/ui/icon.png
Terminal=false
Type=Application
Categories=Game;
EOF
}

if [ "$EUID" -ne 0 ]; then
    echo "Error: Please run with 'sudo' privileges"
    exit 1
fi


if is_supported_distro; then
    if [ "$(detect_distro)" = "nixos" ]; then
        echo "Info: Detected NixOS, using NixOS-specific installation"
        nixos_install
    else
        echo "Info: Detected supported distro, using default installation"
        default_install
    fi
fi