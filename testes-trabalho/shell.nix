{ pkgs ? import <nixpkgs> { } }:

with pkgs;

mkShell rec {
  buildInputs = [ python3 poetry zlib libGL glib libsForQt5.qt5.qtwayland ];

  shellHook = ''
    export LD_LIBRARY_PATH="${
      pkgs.lib.makeLibraryPath buildInputs
    }:$LD_LIBRARY_PATH"
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib.outPath}/lib:$LD_LIBRARY_PATH"
    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:${pkgs.glibc}/lib"
  '';
}
