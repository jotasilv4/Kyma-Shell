#!/bin/bash
set -euo pipefail

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

# Evita executar como root
if [ "$(id -u)" -eq 0 ]; then
    echo "Por favor, não execute este script como root"
    exit 1
fi

# Instala o yay se não estiver instalado
if ! command -v yay &>/dev/null; then
    echo "Instalando o yay..."
    tmpdir=$(mktemp -d)
    git clone https://aur.archlinux.org/yay.git "$tmpdir/yay"
    pushd "$tmpdir/yay" > /dev/null
    makepkg -si --noconfirm
    popd > /dev/null
    rm -rf "$tmpdir"
fi

# Clona ou atualiza o Kyma-Shell
if [ -d "$INSTALL_DIR" ]; then
    echo "Atualizando Kyma-Shell..."
    git -C "$INSTALL_DIR" pull
else
    echo "Clonando Kyma-Shell..."
    git clone "$REPO_URL" "$INSTALL_DIR" -b v1.0.1
fi

# Instala o gray-git
echo "Instalando gray-git..."
yes | yay -Syy --needed --confirm gray-git || true

# Instala os pacotes necessários via yay
echo "Instalando pacotes necessários com yay..."
yay -Syy --needed --noconfirm "${PACKAGES_YAY[@]}" || true

# Instala os pacotes necessários via pacman
echo "Instalando pacotes necessários com pacman..."
sudo pacman -Syy --needed --noconfirm "${PACKAGES_PACMAN[@]}" || true

# Atualiza pacotes desatualizados da lista
echo "Atualizando pacotes necessários desatualizados..."
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
