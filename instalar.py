#!/usr/bin/env python3
"""
Script de Instalação do Aplicativo de Loteamento Urbano
Instala automaticamente todas as dependências necessárias
"""

import subprocess
import sys
import os

def verificar_python():
    """Verifica se a versão do Python é adequada"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("ERRO: Python 3.8 ou superior é necessário.")
        print(f"Versão atual: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detectado")
    return True

def instalar_dependencias():
    """Instala as dependências necessárias"""
    print("\nInstalando dependências...")
    
    dependencias = [
        "customtkinter>=5.2.0",
        "geopandas>=1.0.0", 
        "shapely>=2.0.0",
        "ezdxf>=1.4.0"
    ]
    
    for dep in dependencias:
        print(f"Instalando {dep}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✓ {dep} instalado com sucesso")
        except subprocess.CalledProcessError:
            print(f"✗ Erro ao instalar {dep}")
            return False
    
    return True

def verificar_instalacao():
    """Verifica se todas as dependências foram instaladas corretamente"""
    print("\nVerificando instalação...")
    
    modulos = [
        ("customtkinter", "CustomTkinter"),
        ("geopandas", "GeoPandas"),
        ("shapely", "Shapely"),
        ("ezdxf", "ezdxf")
    ]
    
    for modulo, nome in modulos:
        try:
            __import__(modulo)
            print(f"✓ {nome} disponível")
        except ImportError:
            print(f"✗ {nome} não encontrado")
            return False
    
    return True

def criar_atalho_desktop():
    """Cria um atalho na área de trabalho (Windows)"""
    if sys.platform == "win32":
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "Loteamento Urbano.lnk")
            target = os.path.join(os.getcwd(), "loteamento_app.py")
            wDir = os.getcwd()
            icon = target
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{target}"'
            shortcut.WorkingDirectory = wDir
            shortcut.IconLocation = icon
            shortcut.save()
            
            print("✓ Atalho criado na área de trabalho")
        except:
            print("! Não foi possível criar atalho na área de trabalho")

def main():
    """Função principal de instalação"""
    print("=" * 60)
    print("    INSTALADOR DO APLICATIVO DE LOTEAMENTO URBANO")
    print("=" * 60)
    print()
    
    # Verificar Python
    if not verificar_python():
        input("Pressione Enter para sair...")
        return False
    
    # Instalar dependências
    if not instalar_dependencias():
        print("\nERRO: Falha na instalação das dependências")
        input("Pressione Enter para sair...")
        return False
    
    # Verificar instalação
    if not verificar_instalacao():
        print("\nERRO: Algumas dependências não foram instaladas corretamente")
        input("Pressione Enter para sair...")
        return False
    
    # Criar atalho (opcional)
    criar_atalho_desktop()
    
    print("\n" + "=" * 60)
    print("    INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print()
    print("Para executar o aplicativo:")
    print(f"  python {os.path.join(os.getcwd(), 'loteamento_app.py')}")
    print()
    print("Ou execute diretamente o arquivo 'loteamento_app.py'")
    print()
    
    input("Pressione Enter para sair...")
    return True

if __name__ == "__main__":
    main()

