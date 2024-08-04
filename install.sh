#!/bin/bash

set -e

# ========================================

INSTALL_PATH="${HOME}/.harbor"
REPO_URL="https://github.com/av/harbor.git"

# ========================================

check_dependencies() {
  if ! command -v docker >/dev/null 2>&1 || ! command -v git >/dev/null 2>&1; then
    echo "Error: Docker or Git not found. Please install missing dependencies."
    exit 1
  fi
}

install_or_update_project() {
  if [ -d "$INSTALL_PATH" ]; then
    echo "Existing installation found. Updating..."
    cd "$INSTALL_PATH"
    git pull
  else
    echo "Cloning project repository..."
    git clone "$REPO_URL" "$INSTALL_PATH"
    cd "$INSTALL_PATH"
  fi
}

main() {
  echo "Installing Harbor."

  echo "Checking dependencies..."
  check_dependencies

  echo "Starting installation..."
  install_or_update_project

  ./harbor.sh -v
  ./harbor.sh ln

  echo "Installation complete."
}

main