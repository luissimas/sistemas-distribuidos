{ pkgs ? import <nixpkgs> { } }:

with pkgs;

mkShell { buildInputs = [ python3Packages.pyzmq ]; }
