#!/bin/bash
    
set -e
set -u
set -o pipefail

REPO_URL="https://github.com/jotasilv4/kymashell.git"
INSTALL_DIR="$HOME/.config/Kyma-Shell"
PACKAGES_YAY=(
    fabric-cli-git
    python-fabric-git
    python-setproctitle
    python-i3ipc
)
PACKAGES_PACMAN=(
    picom
)

# Prevent running as root
if [ "$(id -u)" -eq 0 ]; then
    echo "Please do not run this script as root"
    exit 1
fi

# Install yay if not installed
if ! command -v yay &>/dev/null; then
    echo "Installing yay"
    tmpdir=$(mktemp -d)
    git clone https://aur.archlinux.org/yay.git "$tmpdir/yay"
    
    cd "$tmpdir/yay"
    makepkg -si --noconfirm
    
    cd - > /dev/null
    rm -rf "$tmpdir"
fi

if [ -d "$INSTALL_DIR" ]; then
    echo "Updating Kyma-Shell"
    git -C "$INSTALL_DIR" pull
else
    echo "Cloning Kyma-Shell"
    git clone "$REPO_URL" "$INSTALL_DIR" -b v1.0.1
fi

echo "Installing gray-git"
yes | yay -Syy --needed --confirm gray-git || true

# Install required packages using yay
echo "Installing required yay packages..."
yay -Syy --needed --noconfirm "${PACKAGES_YAY[@]}" || true

# Install required packages using pacman
echo "Installing required pacman packages..."
sudo pacman -Syy --needed --noconfirm "${PACKAGES_PACMAN[@]}" || true
    
# Update outdated packages from the list
echo "Updating outdated required packages..."
# Get a list of outdated packages
outdated=$(yay -Qu | awk '{print $1}')
to_update=()
for pkg in "${PACKAGES_YAY[@]}"; do
    if echo "$outdated" | grep -q "^$pkg\$"; then
        to_update+=("$pkg")
    fi
done

if [ ${#to_update[@]} -gt 0 ]; then
    yay -S --noconfirm "${to_update[@]}" || true
else
    echo "All required packages are up-to-date."
fi

# Move picom 
mv $INSTALL_DIR/config/picom $HOME/.config/

# Move systemboot bin
mkdir -p .local/bin/
mv $INSTALL_DIR/config/systemboot $HOME/.local/bin/

# Launch Ax-Shell without terminal output
echo "Starting Ax-Shell..."
killall kima-shell 2>/dev/null || true

echo "exec_always --no-startup-id python $INSTALL_DIR/main.py" >> $HOME/.config/i3/config
python "$INSTALL_DIR/main.py" > /dev/null 2>&1
    
echo "Installation complete."