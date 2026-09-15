{
  description = "Keymap visualization (keymap-drawer) for the Moonlander layout";

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
            root="''${1:-$PWD}"
            mkdir -p "$root/docs"
            python3 "$root/keymap-viz/keymap2yaml.py" "$root/RgoVP/keymap.c" \
              > "$root/keymap-viz/keymap.yaml"
            keymap draw "$root/keymap-viz/keymap.yaml" > "$root/docs/keymap.svg"
            echo "Wrote $root/docs/keymap.svg"
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
