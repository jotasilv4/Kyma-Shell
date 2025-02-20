import os
import glob

def listar_arquivos_desktop():
    # Diretórios padrão onde estão os arquivos .desktop
    diretorios = [
        '/usr/share/applications',
        os.path.expanduser('~/.local/share/applications')
    ]
    arquivos = []
    for d in diretorios:
        if os.path.exists(d):
            arquivos.extend(glob.glob(os.path.join(d, '*.desktop')))
    return arquivos

def parse_desktop_file(caminho_arquivo):
    nome = None
    exec_cmd = None
    icon = None
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as f:
            for linha in f:
                linha = linha.strip()
                if linha.startswith('Name='):
                    nome = linha.split('=', 1)[1]
                elif linha.startswith('Exec='):
                    exec_cmd = linha.split('=', 1)[1]
                elif linha.startswith('Icon='):
                    icon = linha.split('=', 1)[1]
                # Se já encontrou os três, pode sair do loop
                if nome and exec_cmd and icon:
                    break
    except Exception as e:
        print(f"Erro ao ler {caminho_arquivo}: {e}")
    return nome, exec_cmd, icon

def listar_aplicativos():
    arquivos = listar_arquivos_desktop()
    aplicativos = []
    for arquivo in arquivos:
        nome, comando, icon = parse_desktop_file(arquivo)
        if nome:
            aplicativos.append({'nome': nome, 'comando': comando, 'icon': icon, 'arquivo': arquivo})
    return aplicativos

if __name__ == "__main__":
    apps = listar_aplicativos()
    for app in apps:
        print(f"Nome: {app['nome']}")
        print(f"Comando: {app['comando']}")
        print(f"Ícone: {app['icon']}")
        print(f"Arquivo: {app['arquivo']}\n")
