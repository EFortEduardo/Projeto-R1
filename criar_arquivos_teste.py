import ezdxf
import os

def criar_perimetro_teste_retangular(largura=100, altura=80, arquivo_saida="perimetro_teste.dxf"):
    """
    Cria um arquivo DXF de teste com um perímetro retangular simples.
    
    Args:
        largura: Largura do retângulo em metros
        altura: Altura do retângulo em metros
        arquivo_saida: Nome do arquivo DXF de saída
    """
    # Criar novo documento DXF
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    
    # Criar layer para o perímetro
    doc.layers.new('PERIMETRO', dxfattribs={'color': 1})
    
    # Definir coordenadas do retângulo
    coords = [
        (0, 0),
        (largura, 0),
        (largura, altura),
        (0, altura),
        (0, 0)  # Fechar o polígono
    ]
    
    # Adicionar polilinha fechada
    msp.add_lwpolyline(coords, close=True, dxfattribs={'layer': 'PERIMETRO'})
    
    # Salvar arquivo
    doc.saveas(arquivo_saida)
    print(f"Arquivo DXF criado: {arquivo_saida}")
    print(f"Perímetro retangular: {largura}m x {altura}m")
    print(f"Área total: {largura * altura} m²")

def criar_perimetro_teste_irregular(arquivo_saida="perimetro_irregular_teste.dxf"):
    """
    Cria um arquivo DXF de teste com um perímetro irregular.
    
    Args:
        arquivo_saida: Nome do arquivo DXF de saída
    """
    # Criar novo documento DXF
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    
    # Criar layer para o perímetro
    doc.layers.new('PERIMETRO', dxfattribs={'color': 1})
    
    # Definir coordenadas de um polígono irregular
    coords = [
        (0, 0),
        (120, 0),
        (120, 60),
        (100, 80),
        (80, 90),
        (40, 85),
        (20, 70),
        (0, 50),
        (0, 0)  # Fechar o polígono
    ]
    
    # Adicionar polilinha fechada
    msp.add_lwpolyline(coords, close=True, dxfattribs={'layer': 'PERIMETRO'})
    
    # Salvar arquivo
    doc.saveas(arquivo_saida)
    print(f"Arquivo DXF criado: {arquivo_saida}")
    print("Perímetro irregular criado para teste")

def criar_perimetro_teste_complexo(arquivo_saida="perimetro_complexo_teste.dxf"):
    """
    Cria um arquivo DXF de teste com um perímetro mais complexo.
    
    Args:
        arquivo_saida: Nome do arquivo DXF de saída
    """
    # Criar novo documento DXF
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    
    # Criar layer para o perímetro
    doc.layers.new('PERIMETRO', dxfattribs={'color': 1})
    
    # Definir coordenadas de um polígono em forma de "L"
    coords = [
        (0, 0),
        (150, 0),
        (150, 80),
        (80, 80),
        (80, 120),
        (0, 120),
        (0, 0)  # Fechar o polígono
    ]
    
    # Adicionar polilinha fechada
    msp.add_lwpolyline(coords, close=True, dxfattribs={'layer': 'PERIMETRO'})
    
    # Salvar arquivo
    doc.saveas(arquivo_saida)
    print(f"Arquivo DXF criado: {arquivo_saida}")
    print("Perímetro em forma de 'L' criado para teste")

if __name__ == "__main__":
    # Criar diretório de assets se não existir
    assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    # Criar arquivos de teste
    criar_perimetro_teste_retangular(
        largura=100, 
        altura=80, 
        arquivo_saida=os.path.join(assets_dir, "perimetro_retangular.dxf")
    )
    
    criar_perimetro_teste_irregular(
        arquivo_saida=os.path.join(assets_dir, "perimetro_irregular.dxf")
    )
    
    criar_perimetro_teste_complexo(
        arquivo_saida=os.path.join(assets_dir, "perimetro_complexo.dxf")
    )
    
    print("\nTodos os arquivos de teste foram criados no diretório 'assets'.")
    print("Use estes arquivos para testar o aplicativo de loteamento.")

