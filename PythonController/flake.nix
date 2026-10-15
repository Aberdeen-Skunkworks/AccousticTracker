{
  inputs = {
    nixpkgs.url = github:NixOS/nixpkgs/nixos-25.05;
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }: 
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          #overlays = [ self.overlays.default ];
        };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            bashInteractive
            git
            libsForQt5.qt5.qtbase
            (python3.withPackages (ps: with ps; [
              matplotlib
              numpy
              pyqt5
              openpyxl
              mido
              pyserial
            ]))
          ];
          QT_PLUGIN_PATH = "${pkgs.qt5.qtbase.qtPluginPrefix}";
        };
      })  
  ;
}