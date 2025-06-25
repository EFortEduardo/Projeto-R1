#!/usr/bin/env python3
"""
Teste completo do processador robusto para verificar se os erros foram corrigidos
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from loteamento_processor_robusto import LoteamentoProcessorRobusto

def teste_processamento_completo():
    """Testa o processamento completo com o processador robusto"""
    print("=" * 60)
    print("TESTE COMPLETO DO PROCESSADOR ROBUSTO")
    print("=" * 60)
    
    # Parâmetros de teste
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
    arquivo_saida = os.path.join("output", "teste_completo_robusto.dxf")
    
    # Verificar se arquivo de entrada existe
    if not os.path.exists(arquivo_entrada):
        print(f"ERRO: Arquivo de entrada não encontrado: {arquivo_entrada}")
        return False
    
    # Criar diretório de saída
    os.makedirs("output", exist_ok=True)
    
    print(f"Arquivo de entrada: {arquivo_entrada}")
    print(f"Arquivo de saída: {arquivo_saida}")
    print()
    
    try:
        # Usar o método de processamento completo
        print("Executando processamento completo...")
        processor = LoteamentoProcessorRobusto(parametros)
        
        resultado = processor.processar_loteamento_robusto(arquivo_entrada, arquivo_saida)
        
        if resultado['sucesso']:
            print("✅ Processamento concluído com sucesso!")
            print()
            print("📊 ESTATÍSTICAS:")
            print(f"   Área total: {resultado['area_total']:.2f} m²")
            print(f"   Lotes criados: {resultado['num_lotes']}")
            print(f"   Área dos lotes: {resultado['area_lotes']:.2f} m² ({resultado['percentual_lotes']:.1f}%)")
            print(f"   Área das ruas: {resultado['area_ruas']:.2f} m² ({resultado['percentual_ruas']:.1f}%)")
            print(f"   Área verde: {resultado['area_verde']:.2f} m² ({resultado['percentual_verde']:.1f}%)")
            print(f"   Área institucional: {resultado['area_institucional']:.2f} m² ({resultado['percentual_institucional']:.1f}%)")
            print(f"   Arquivo DXF salvo: {arquivo_saida}")
            
            # Verificar se o arquivo foi criado
            if os.path.exists(arquivo_saida):
                print(f"✅ Arquivo DXF criado com sucesso: {os.path.getsize(arquivo_saida)} bytes")
            else:
                print("❌ Arquivo DXF não foi criado")
                return False
            
            return True
        else:
            print(f"❌ Erro no processamento: {resultado['erro']}")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def teste_diferentes_arquivos():
    """Testa o processamento com diferentes arquivos"""
    print("\n" + "=" * 60)
    print("TESTE COM DIFERENTES ARQUIVOS")
    print("=" * 60)
    
    parametros = {
        'largura_rua': 8.0,
        'largura_calcada': 2.0,
        'profundidade_max_quadra': 60.0,
        'orientacao_preferencial': 'Automática',
        'area_minima_lote': 200.0,
        'testada_minima_lote': 8.0,
        'largura_padrao_lote': 12.0,
        'profundidade_padrao_lote': 30.0,
        'percentual_area_verde': 10.0,
        'percentual_area_institucional': 5.0
    }
    
    arquivos_teste = [
        ("assets/perimetro_retangular.dxf", "output/teste_retangular_robusto.dxf", "Retangular"),
        ("assets/perimetro_irregular.dxf", "output/teste_irregular_robusto.dxf", "Irregular"),
        ("assets/perimetro_complexo.dxf", "output/teste_complexo_robusto.dxf", "Complexo")
    ]
    
    sucessos = 0
    total = len(arquivos_teste)
    
    for arquivo_entrada, arquivo_saida, descricao in arquivos_teste:
        print(f"\nTestando {descricao}: {arquivo_entrada}")
        print("-" * 40)
        
        if not os.path.exists(arquivo_entrada):
            print(f"❌ Arquivo não encontrado: {arquivo_entrada}")
            continue
        
        try:
            processor = LoteamentoProcessorRobusto(parametros)
            resultado = processor.processar_loteamento_robusto(arquivo_entrada, arquivo_saida)
            
            if resultado['sucesso']:
                print(f"✅ {descricao} processado com sucesso!")
                print(f"   Lotes: {resultado['num_lotes']}")
                print(f"   Área total: {resultado['area_total']:.2f} m²")
                sucessos += 1
            else:
                print(f"❌ Erro no {descricao}: {resultado['erro']}")
                
        except Exception as e:
            print(f"❌ Erro ao processar {descricao}: {e}")
    
    print(f"\n📊 Resultado: {sucessos}/{total} arquivos processados com sucesso")
    return sucessos == total

def main():
    """Função principal dos testes"""
    print("INICIANDO TESTE COMPLETO DO PROCESSADOR ROBUSTO")
    print("Data/Hora:", __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Mudar para o diretório do script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Executar testes
    teste1_ok = teste_processamento_completo()
    teste2_ok = teste_diferentes_arquivos()
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES COMPLETOS")
    print("=" * 60)
    print(f"Teste de processamento completo: {'✅ PASSOU' if teste1_ok else '❌ FALHOU'}")
    print(f"Teste com diferentes arquivos: {'✅ PASSOU' if teste2_ok else '❌ FALHOU'}")
    
    todos_passaram = teste1_ok and teste2_ok
    
    if todos_passaram:
        print("\n🎉 TODOS OS TESTES COMPLETOS PASSARAM!")
        print("O processador robusto está funcionando corretamente.")
        print("Os erros de importação e método inexistente foram corrigidos.")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM!")
        print("Verifique os erros acima.")
    
    return todos_passaram

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)

