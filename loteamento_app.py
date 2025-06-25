#!/usr/bin/env python3
"""
Aplicativo de Loteamento Urbano
Desenvolvido com base no plano de desenvolvimento fornecido

Este aplicativo permite:
- Carregar perímetros de terrenos (.dxf ou .kml)
- Configurar parâmetros de loteamento
- Gerar automaticamente lotes, quadras, ruas e áreas comuns
- Exportar resultado em formato DXF para CAD

Autor: Desenvolvido conforme especificações do cliente
Tecnologias: Python, CustomTkinter, GeoPandas, Shapely, ezdxf
"""

import sys
import os

# Adicionar o diretório src ao path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from main_gui import LoteamentoApp
    
    def main():
        """Função principal do aplicativo"""
        print("=" * 60)
        print("    APLICATIVO DE LOTEAMENTO URBANO")
        print("=" * 60)
        print("Inicializando interface gráfica...")
        print("Aguarde...")
        print()
        
        # Criar e executar aplicativo
        app = LoteamentoApp()
        app.run()
        
        print("Aplicativo encerrado.")
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print("ERRO: Dependências não encontradas.")
    print(f"Detalhes: {e}")
    print()
    print("Para instalar as dependências necessárias, execute:")
    print("pip install customtkinter geopandas shapely ezdxf")
    sys.exit(1)
    
except Exception as e:
    print(f"ERRO: {e}")
    sys.exit(1)

