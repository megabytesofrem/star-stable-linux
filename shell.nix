{ pkgs ? import <nixpkgs> {} }:

(pkgs.buildFHSEnv {
  name = "sso-wine-env";

  privateIPC = false;
  privateNetwork = false;

  targetPkgs = pkgs: with pkgs; [
    # -- Runtime dependencies for the launcher --
    (python3.withPackages (ps: with ps; [
      pyqt6
    ])) 

    # -- KDE Breeze Theme Support Engine --
    kdePackages.breeze
    kdePackages.breeze-icons
    kdePackages.qqc2-breeze-style
    kdePackages.qqc2-desktop-style  # Ensures fallback framework links exist

    # -- Wine --
    wineWow64Packages.stable
    winetricks
    curl    
    mesa
    vulkan-loader
    vulkan-tools
    
    # -- 32 bit support for Star Stable --
    pkgsi686Linux.mesa
    pkgsi686Linux.vulkan-loader

    libpulseaudio
    pipewire
    alsa-lib
  ];
  
  multiPkgs = pkgs: with pkgs; [
    libx11
    libxext
    libxcursor
    libxrandr
    libxi
  ];

  runScript = pkgs.writeScript "init.sh" ''
    #!/usr/bin/env bash
    chmod +x scripts/star-stable-linux.sh
    python3 star-stable-linux-gui.py
    # exec ./scripts/star-stable-linux.sh
  '';
}).env