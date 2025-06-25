#!/usr/bin/env python3
"""
Teste específico para verificar o carregamento de arquivos KML e DXF
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from loteamento_processor_robusto import LoteamentoProcessorRobusto

def teste_carregamento_arquivos():
    """Testa o carregamento de diferentes tipos de arquivo"""
    print("=" * 60)
    print("TESTE DE CARREGAMENTO DE ARQUIVOS")
    print("=" * 60)
    
    # Parâmetros básicos
    parametros = {
        'largura_rua': 8.0,
        'largura_calcada': 2.0,
        'profundidade_max_quadra': 80.0,
        'orientacao_preferencial': 'Automática',
        'area_minima_lote': 200.0,
        'testada_minima_lote': 8.0,
        'largura_padrao_lote': 12.0,
        'profundidade_padrao_lote': 30.0,
        'percentual_area_verde': 15.0,
        'percentual_area_institucional': 5.0
    }
    
    processor = LoteamentoProcessorRobusto(parametros)
    
    # Arquivos de teste
    arquivos_teste = [
        ("assets/perimetro_retangular.dxf", "DXF Retangular"),
        ("assets/perimetro_irregular.dxf", "DXF Irregular"),
        ("assets/perimetro_complexo.dxf", "DXF Complexo")
    ]
    
    sucessos = 0
    total = len(arquivos_teste)
    
    for arquivo, descricao in arquivos_teste:
        print(f"\nTestando {descricao}: {arquivo}")
        print("-" * 40)
        
        if not os.path.exists(arquivo):
            print(f"❌ Arquivo não encontrado: {arquivo}")
            continue
            
        try:
            resultado = processor.carregar_perimetro(arquivo)
            if resultado:
                print(f"✅ {descricao} carregado com sucesso!")
                print(f"   Área: {processor.perimetro_original.area:.2f} m²")
                print(f"   Válido: {processor.perimetro_original.is_valid}")
                sucessos += 1
            else:
                print(f"❌ Falha ao carregar {descricao}")
        except Exception as e:
            print(f"❌ Erro ao carregar {descricao}: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"RESULTADO: {sucessos}/{total} arquivos carregados com sucesso")
    
    return sucessos == total

def teste_arquivo_inexistente():
    """Testa o comportamento com arquivo inexistente"""
    print("\n" + "=" * 60)
    print("TESTE DE ARQUIVO INEXISTENTE")
    print("=" * 60)
    
    processor = LoteamentoProcessorRobusto({})
    
    arquivo_inexistente = "arquivo_que_nao_existe.dxf"
    print(f"Testando arquivo inexistente: {arquivo_inexistente}")
    
    try:
        resultado = processor.carregar_perimetro(arquivo_inexistente)
        if not resultado:
            print("✅ Arquivo inexistente tratado corretamente")
            return True
        else:
            print("❌ Arquivo inexistente deveria retornar False")
            return False
    except Exception as e:
        print(f"❌ Erro inesperado com arquivo inexistente: {e}")
        return False

def teste_extensao_invalida():
    """Testa o comportamento com extensão inválida"""
    print("\n" + "=" * 60)
    print("TESTE DE EXTENSÃO INVÁLIDA")
    print("=" * 60)
    
    processor = LoteamentoProcessorRobusto({})
    
    # Criar arquivo temporário com extensão inválida
    arquivo_invalido = "teste_invalido.txt"
    
    try:
        with open(arquivo_invalido, 'w') as f:
            f.write("Este é um arquivo de texto, não um arquivo geoespacial")
        
        print(f"Testando arquivo com extensão inválida: {arquivo_invalido}")
        
        resultado = processor.carregar_perimetro(arquivo_invalido)
        
        # Limpar arquivo temporário
        os.remove(arquivo_invalido)
        
        if not resultado:
            print("✅ Extensão inválida tratada corretamente")
            return True
        else:
            print("❌ Extensão inválida deveria retornar False")
            return False
            
    except Exception as e:
        # Limpar arquivo temporário em caso de erro
        if os.path.exists(arquivo_invalido):
            os.remove(arquivo_invalido)
        print(f"❌ Erro inesperado com extensão inválida: {e}")
        return False

def main():
    """Função principal dos testes"""
    print("INICIANDO TESTES DE CARREGAMENTO DE ARQUIVOS")
    print("Data/Hora:", __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Mudar para o diretório do script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Executar testes
    teste1_ok = teste_carregamento_arquivos()
    teste2_ok = teste_arquivo_inexistente()
    teste3_ok = teste_extensao_invalida()
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES DE CARREGAMENTO")
    print("=" * 60)
    print(f"Teste de carregamento de arquivos: {'✅ PASSOU' if teste1_ok else '❌ FALHOU'}")
    print(f"Teste de arquivo inexistente: {'✅ PASSOU' if teste2_ok else '❌ FALHOU'}")
    print(f"Teste de extensão inválida: {'✅ PASSOU' if teste3_ok else '❌ FALHOU'}")
    
    todos_passaram = teste1_ok and teste2_ok and teste3_ok
    
    if todos_passaram:
        print("\n🎉 TODOS OS TESTES DE CARREGAMENTO PASSARAM!")
        print("O carregamento de arquivos está funcionando corretamente.")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM!")
        print("Verifique os erros acima.")
    
    return todos_passaram

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)

