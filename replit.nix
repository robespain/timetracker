
{ pkgs }: {
  deps = [
    pkgs.python3
    pkgs.python3Packages.pip
    pkgs.postgresql
    pkgs.openssl
    pkgs.zlib
    pkgs.pkg-config
    pkgs.which
  ];
}
