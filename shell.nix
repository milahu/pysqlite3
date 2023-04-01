{
  pkgs ? import <nixpkgs> {}
}:

let
  python = pkgs.python3.withPackages (pp: with pp; [
    #requests
    kaitaistruct
    pytest # test runner
    black # code formatter
  ]);
  kaitai-struct-compiler = pkgs.callPackage ./nix/kaitai-struct-compiler.nix { };
in

pkgs.mkShell {

  buildInputs = (with pkgs; [
    #gnumake
    kaitai-struct-compiler
  ]) ++ [
    python
  ];

}
