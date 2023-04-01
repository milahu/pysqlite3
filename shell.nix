{
  pkgs ? import <nixpkgs> {}
}:

let
  pythonWithPackages = pkgs.python3.withPackages (pp: with pp; [
    #requests
    kaitaistruct
    sqlglot
    pytest # test runner
    black # code formatter
  ]);
  kaitai-struct-compiler = pkgs.callPackage ./nix/kaitai-struct-compiler.nix { };
  extraPythonPackages = {
    sqltree = pkgs.callPackage ./nix/sqltree.nix { };
    sqloxide = pkgs.callPackage ./nix/sqloxide.nix { };
  };
in

pkgs.mkShell {

  buildInputs = (with pkgs; [
    #gnumake
    kaitai-struct-compiler
  ]) ++ [
    pythonWithPackages
  ];

}
