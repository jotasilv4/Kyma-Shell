#!/bin/bash
set -euo pipefail

REPO_URL="https://github.com/jotasilv4/kymashell.git"
INSTALL_DIR="$HOME/.config/Kyma-Shell"
PACKAGES_YAY=(
    fabric-cli-git
    python-fabric-git
    python-setproctitle
    python-i3ipc
    python-toml
    python-watchdog
    python-pillow
    ttf-tabler-icons
    matugen-bin
    libnotify
    playerctl
    vte3
    gtk3
    gnome-bluetooth-3.0
    cava
    acpi
    brightnessctl
)
PACKAGES_PACMAN=(
    picom
    nitrogen
)

# Evita executar como root
if [ "$(id -u)" -eq 0 ]; then
    echo "Por favor, não execute este script como root"
    exit 1
fi


aur_helper=""
if command -v yay &>/dev/null; then
    aur_helper="yay"
    echo $aur_helper
elif command -v paru &>/dev/null; then
    aur_helper="paru"
    echo $aur_helper
else
    echo "Installing yay-bin..."
    tmpdir=$(mktemp -d)
    git clone https://aur.archlinux.org/yay-bin.git "$tmpdir/yay-bin"
    cd "$tmpdir/yay-bin"
    makepkg -si --noconfirm
    cd - > /dev/null
    rm -rf "$tmpdir"
    aur_helper="yay"
fi

# Clona ou atualiza o Kyma-Shell
if [ -d "$INSTALL_DIR" ]; then
    echo "Atualizando Kyma-Shell..."
    git -C "$INSTALL_DIR" pull
else
    echo "Clonando Kyma-Shell..."
    git clone "$REPO_URL" "$INSTALL_DIR" -b dev
fi

# Instala os pacotes necessários via yay
echo "Instalando pacotes necessários com yay..."
$aur_helper -Syy --needed --noconfirm "${PACKAGES_YAY[@]}" || true


# Instala os pacotes necessários via pacman
echo "Instalando pacotes necessários com pacman..."
sudo pacman -Syy --needed --noconfirm "${PACKAGES_PACMAN[@]}" || true
    
# Instala o gray-git
echo "Instalando gray-git..."
yes | $aur_helper -Syy --needed --confirm gray-git || true

# Atualiza pacotes desatualizados da lista
echo "Atualizando pacotes necessários desatualizados..."
outdated=$($aur_helper -Qu | awk '{print $1}')
to_update=()
for pkg in "${PACKAGES_YAY[@]}"; do
    if echo "$outdated" | grep -q "^$pkg\$"; then
        to_update+=("$pkg")
    fi
done

if [ ${#to_update[@]} -gt 0 ]; then
    $aur_helper -S --noconfirm "${to_update[@]}" || true
else
    echo "Todos os pacotes necessários estão atualizados."
fi

# Substitui a configuração do picom, se disponível
if [ -d "$INSTALL_DIR/config/picom" ]; then
    [ -d "$HOME/.config/picom" ] && rm -rf "$HOME/.config/picom"
    cp -r "$INSTALL_DIR/config/picom" "$HOME/.config/"
fi

# Move o binário systemboot, se existir
if [ -e "$INSTALL_DIR/config/systemboot" ]; then
    mkdir -p "$HOME/.local/bin/"
    cp "$INSTALL_DIR/config/systemboot" "$HOME/.local/bin/"
    chmod +x "$HOME/.local/bin/systemboot"
fi

# Adiciona o comando de inicialização no i3 config, se ainda não existir
I3_CONFIG="$HOME/.config/i3/config"
LAUNCH_CMD="exec_always --no-startup-id python $INSTALL_DIR/main.py"
if [ -f "$I3_CONFIG" ]; then
    if ! grep -Fxq "$LAUNCH_CMD" "$I3_CONFIG"; then
        echo "$LAUNCH_CMD" >> "$I3_CONFIG"
    fi
else
    echo "$LAUNCH_CMD" > "$I3_CONFIG"
fi

# Encerra instâncias do Kyma-Shell (corrigindo o nome do processo) e inicia-o
echo "Iniciando Kyma-Shell..."
killall kyma-shell 2>/dev/null || true
python "$INSTALL_DIR/main.py" > /dev/null 2>&1

echo "Instalação completa."
