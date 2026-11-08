#!/bin/sh
# Install docile: downloads the latest release binary for this machine.
#   curl -fsSL https://raw.githubusercontent.com/aliemrenebiler/docile/main/install.sh | sh
# Options (environment): DOCILE_INSTALL_DIR (default ~/.local/bin),
#                        DOCILE_BASE_URL (default: latest GitHub release)
set -eu

REPO="aliemrenebiler/docile"
BASE_URL="${DOCILE_BASE_URL:-https://github.com/$REPO/releases/latest/download}"
INSTALL_DIR="${DOCILE_INSTALL_DIR:-$HOME/.local/bin}"

die() { echo "Error: $*" >&2; exit 1; }

case "$(uname -s)" in
  Darwin) os=darwin ;;
  Linux) os=linux ;;
  *) die "unsupported OS: $(uname -s) (macOS and Linux only)" ;;
esac
case "$(uname -m)" in
  arm64 | aarch64) if [ "$os" = darwin ]; then arch=arm64; else arch=aarch64; fi ;;
  x86_64 | amd64) arch=x86_64 ;;
  *) die "unsupported CPU: $(uname -m)" ;;
esac
asset="docile-$os-$arch"

if command -v curl >/dev/null 2>&1; then
  fetch() { curl -fsSL "$1" -o "$2"; }
elif command -v wget >/dev/null 2>&1; then
  fetch() { wget -q "$1" -O "$2"; }
else
  die "curl or wget is required"
fi

if command -v sha256sum >/dev/null 2>&1; then
  sha() { sha256sum "$1" | cut -d' ' -f1; }
elif command -v shasum >/dev/null 2>&1; then
  sha() { shasum -a 256 "$1" | cut -d' ' -f1; }
else
  die "sha256sum or shasum is required"
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

echo "Downloading $asset ..."
fetch "$BASE_URL/$asset" "$tmp/$asset" || die "download failed: $BASE_URL/$asset"
fetch "$BASE_URL/SHA256SUMS" "$tmp/SHA256SUMS" || die "download failed: $BASE_URL/SHA256SUMS"

expected="$(awk -v a="$asset" '$2 == a { print $1 }' "$tmp/SHA256SUMS")"
[ -n "$expected" ] || die "no checksum for $asset in the release"
[ "$(sha "$tmp/$asset")" = "$expected" ] || die "checksum mismatch, nothing installed"

mkdir -p "$INSTALL_DIR"
chmod +x "$tmp/$asset"
mv "$tmp/$asset" "$INSTALL_DIR/docile"
echo "Installed: $INSTALL_DIR/docile"

case ":$PATH:" in
  *":$INSTALL_DIR:"*) echo "Run: docile -h" ;;
  *)
    echo
    echo "$INSTALL_DIR is not on your PATH. Add it, then open a new terminal:"
    case "${SHELL:-}" in
      */zsh) echo "  echo 'export PATH=\"$INSTALL_DIR:\$PATH\"' >> ~/.zshrc" ;;
      */bash) echo "  echo 'export PATH=\"$INSTALL_DIR:\$PATH\"' >> ~/.bashrc" ;;
      *) echo "  export PATH=\"$INSTALL_DIR:\$PATH\"   (add to your shell profile)" ;;
    esac
    ;;
esac
