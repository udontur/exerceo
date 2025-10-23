# Turtle use NixOS, so need this file

let
  system = "x86_64-linux";
  pkgs = import <nixpkgs> {
    inherit system;
  };
in [
  pkgs.zstd
  pkgs.gcc-unwrapped
  pkgs.gcc.cc
  pkgs.glibc
  pkgs.zlib
]
