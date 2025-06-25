#!/usr/bin/env python3
"""
Teste abrangente do processador robusto com casos extremos e valores NaN
"""

import sys
import os
import math

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from loteamento_processor_robusto import LoteamentoProcessorRobusto

def teste_valores_nan():
    """Testa o processador com valores NaN e extremos"""
    print("=" * 60)
    print("TESTE DE ROBUSTEZ - VALORES NaN E EXTREMOS")
    print("=" * 60)
    
    # Parâmetros com valores problemáticos
    parametros_problematicos = {
        'largura_rua': float('nan'),  # NaN
        'largura_calcada': float('inf'),  # Infinito
        'profundidade_max_quadra': -50.0,  # Negativo
        'orientacao_preferencial': None,  # None
        'area_minima_lote': 0,  # Zero
        'testada_minima_lote': float('nan'),  # NaN
        'largura_padrao_lote': 1000000,  # Muito grande
        'profundidade_padrao_lote': -10,  # Negativo
        'percentual_area_verde': float('nan'),  # NaN
        'percentual_area_institucional': 150.0  # Maior que 100%
    }
    
    try:
        print("Testando processador com parâmetros problemáticos...")
        processor = LoteamentoProcessorRobusto(parametros_problematicos)
        
        # Verificar se os parâmetros foram corrigidos
        print("Parâmetros corrigidos:")
        for chave, valor in processor.parametros.items():
            print(f"  {chave}: {valor}")
        
        # Verificar se todos os valores são válidos
        todos_validos = True
        for chave, valor in processor.parametros.items():
            if isinstance(valor, (int, float)):
                if math.isnan(valor) or math.isinf(valor) or valor < 0:
                    print(f"ERRO: Valor ainda inválido para {chave}: {valor}")
                    todos_validos = False
        
        if todos_validos:
            print("✓ Todos os parâmetros foram corrigidos com sucesso!")
        else:
            print("✗ Alguns parâmetros ainda estão inválidos")
            return False
            
        return True
        
    except Exception as e:
        print(f"ERRO no teste de valores NaN: {e}")
        return False

def teste_processamento_robusto():
    """Testa o processamento completo com o processador robusto"""
    print("\n" + "=" * 60)
    print("TESTE DE PROCESSAMENTO ROBUSTO")
    print("=" * 60)
    
    # Parâmetros válidos
    parametros = {
        'largura_rua': 8.0,
        'largura_calcada': 2.0,
        'profundidade_max_quadra': 40.0,
        'orientacao_preferencial': 'Automática',
        'area_minima_lote': 200.0,
        'testada_minima_lote': 8.0,
        'largura_padrao_lote': 12.0,
        'profundidade_padrao_lote': 25.0,
        'percentual_area_verde': 15.0,
        'percentual_area_institucional': 5.0
    }
    
    # Arquivos
    arquivo_entrada = os.path.join("assets", "perimetro_retangular.dxf")
    arquivo_saida = os.path.join("output", "teste_robusto_resultado.dxf")
    
    if not os.path.exists(arquivo_entrada):
        print(f"ERRO: Arquivo de entrada não encontrado: {arquivo_entrada}")
        return False
    
    os.makedirs("output", exist_ok=True)
    
    try:
        print("Executando processamento robusto...")
        processor = LoteamentoProcessorRobusto(parametros)
        
        resultado = processor.processar_loteamento_robusto(arquivo_entrada, arquivo_saida)
        
        if resultado['sucesso']:
            print("✓ Processamento concluído com sucesso!")
            print(f"  Lotes criados: {resultado['num_lotes']}")
            print(f"  Área dos lotes: {resultado['area_lotes']:.2f} m²")
            print(f"  Arquivo salvo: {arquivo_saida}")
            return True
        else:
            print(f"✗ Erro no processamento: {resultado['erro']}")
            return False
            
    except Exception as e:
        print(f"ERRO no teste de processamento: {e}")
        import traceback
        traceback.print_exc()
        return False

def teste_validacao_numeros():
    """Testa a validação de números"""
    print("\n" + "=" * 60)
    print("TESTE DE VALIDAÇÃO DE NÚMEROS")
    print("=" * 60)
    
    processor = LoteamentoProcessorRobusto({})
    
    # Casos de teste
    casos_teste = [
        (5.0, "numero_normal", True),
        (float('nan'), "numero_nan", False),
        (float('inf'), "numero_inf", False),
        (-5.0, "numero_negativo", False),
        ("5.5", "string_valida", True),
        ("abc", "string_invalida", False),
        ("", "string_vazia", False),
        (None, "valor_none", False),
        (0, "zero", False),  # Menor que mínimo padrão (0.1)
        (10000, "muito_grande", False)  # Maior que máximo padrão
    ]
    
    sucessos = 0
    total = len(casos_teste)
    
    for valor, nome, deve_passar in casos_teste:
        try:
            resultado = processor._validar_numero(valor, nome)
            if deve_passar:
                print(f"✓ {nome}: {valor} → {resultado}")
                sucessos += 1
            else:
                print(f"✗ {nome}: {valor} deveria falhar mas passou → {resultado}")
        except ValueError as e:
            if not deve_passar:
                print(f"✓ {nome}: {valor} falhou como esperado → {e}")
                sucessos += 1
            else:
                print(f"✗ {nome}: {valor} deveria passar mas falhou → {e}")
        except Exception as e:
            print(f"✗ {nome}: {valor} erro inesperado → {e}")
    
    print(f"\nResultado: {sucessos}/{total} testes passaram")
    return sucessos == total

def teste_arquivo_corrompido():
    """Testa o carregamento de arquivo com dados corrompidos"""
    print("\n" + "=" * 60)
    print("TESTE DE ARQUIVO CORROMPIDO")
    print("=" * 60)
    
    # Criar arquivo DXF com coordenadas problemáticas
    import ezdxf
    
    arquivo_corrompido = os.path.join("output", "arquivo_corrompido.dxf")
    os.makedirs("output", exist_ok=True)
    
    try:
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        
        # Coordenadas com valores problemáticos
        coords_problematicas = [
            (0, 0),
            (100, 0),
            (float('nan'), 50),  # Coordenada NaN
            (100, float('inf')),  # Coordenada infinita
            (0, 100),
            (0, 0)
        ]
        
        msp.add_lwpolyline(coords_problematicas, close=True)
        doc.saveas(arquivo_corrompido)
        
        print(f"Arquivo corrompido criado: {arquivo_corrompido}")
        
        # Tentar carregar com o processador robusto
        processor = LoteamentoProcessorRobusto({})
        resultado = processor.carregar_perimetro(arquivo_corrompido)
        
        if resultado:
            print("✓ Processador conseguiu lidar com arquivo corrompido")
            print(f"  Área do perímetro: {processor.perimetro_original.area:.2f} m²")
            return True
        else:
            print("✓ Processador rejeitou arquivo corrompido adequadamente")
            return True
            
    except Exception as e:
        print(f"Erro no teste de arquivo corrompido: {e}")
        return False

def main():
    """Função principal dos testes"""
    print("INICIANDO TESTES DE ROBUSTEZ")
    print("Data/Hora:", __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Mudar para o diretório do script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Executar testes
    teste1_ok = teste_valores_nan()
    teste2_ok = teste_processamento_robusto()
    teste3_ok = teste_validacao_numeros()
    teste4_ok = teste_arquivo_corrompido()
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES DE ROBUSTEZ")
    print("=" * 60)
    print(f"Teste de valores NaN: {'✓ PASSOU' if teste1_ok else '✗ FALHOU'}")
    print(f"Teste de processamento robusto: {'✓ PASSOU' if teste2_ok else '✗ FALHOU'}")
    print(f"Teste de validação de números: {'✓ PASSOU' if teste3_ok else '✗ FALHOU'}")
    print(f"Teste de arquivo corrompido: {'✓ PASSOU' if teste4_ok else '✗ FALHOU'}")
    
    todos_passaram = teste1_ok and teste2_ok and teste3_ok and teste4_ok
    
    if todos_passaram:
        print("\n🎉 TODOS OS TESTES DE ROBUSTEZ PASSARAM!")
        print("O aplicativo está protegido contra erros NaN e valores inválidos.")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM!")
        print("Verifique os erros acima.")
    
    return todos_passaram

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)

