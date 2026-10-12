{
  description = "Keymap visualization (keymap-drawer) for the Moonlander and Ferris layouts";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        draw = pkgs.writeShellApplication {
          name = "draw-keymap";
          runtimeInputs = [ pkgs.keymap-drawer pkgs.python3 ];
          text = ''
            # CI pins the same keymap-drawer version (build-ferris.yml) so the SVGs match.
            root="''${1:-$PWD}"
            bash "$root/keymap-viz/draw.sh" "$root"
          '';
        };
      in
      {
        packages.default = draw;
        apps.default = {
          type = "app";
          program = "${draw}/bin/draw-keymap";
        };
        devShells.default = pkgs.mkShell {
          packages = [ pkgs.keymap-drawer pkgs.python3 ];
        };
      });
}
