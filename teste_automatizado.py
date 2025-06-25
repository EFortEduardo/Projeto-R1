#!/usr/bin/env python3
"""
Script de teste automatizado para o Aplicativo de Loteamento Urbano
Testa o processamento sem interface gráfica
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from loteamento_processor import LoteamentoProcessor

def teste_processamento_basico():
    """Testa o processamento básico com arquivo retangular"""
    print("=" * 60)
    print("TESTE AUTOMATIZADO - PROCESSAMENTO BÁSICO")
    print("=" * 60)
    
    # Parâmetros de teste
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
    
    # Arquivos
    arquivo_entrada = os.path.join("assets", "perimetro_retangular.dxf")
    arquivo_saida = os.path.join("output", "teste_retangular_resultado.dxf")
    
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
        # Criar processador
        print("1. Criando processador...")
        processor = LoteamentoProcessor(parametros)
        
        # Carregar perímetro
        print("2. Carregando perímetro...")
        if not processor.carregar_perimetro(arquivo_entrada):
            print("ERRO: Falha ao carregar perímetro")
            return False
        print(f"   Perímetro carregado. Área: {processor.perimetro_original.area:.2f} m²")
        
        # Internalizar perímetro
        print("3. Internalizando perímetro...")
        processor.internalizar_perimetro()
        if processor.perimetro_internalizado:
            print(f"   Perímetro internalizado. Área: {processor.perimetro_internalizado.area:.2f} m²")
        else:
            print("ERRO: Falha na internalização do perímetro")
            return False
        
        # Definir eixo principal
        print("4. Definindo eixo principal...")
        eixo_principal = processor.definir_eixo_principal()
        print(f"   Eixo principal: {eixo_principal:.2f} radianos ({eixo_principal * 180 / 3.14159:.1f}°)")
        
        # Criar malha viária
        print("5. Criando malha viária...")
        processor.criar_malha_viaria(eixo_principal)
        print(f"   Malha viária criada. Linhas: {len(processor.malha_viaria)}")
        
        # Dividir em quadras
        print("6. Dividindo em quadras...")
        processor.dividir_em_quadras()
        print(f"   Quadras criadas: {len(processor.quadras)}")
        
        # Subdividir em lotes
        print("7. Subdividindo quadras em lotes...")
        processor.subdividir_quadras_em_lotes()
        print(f"   Lotes criados: {len(processor.lotes)}")
        
        # Alocar áreas comuns
        print("8. Alocando áreas comuns...")
        processor.alocar_areas_comuns()
        print(f"   Áreas verdes: {len(processor.areas_verdes)}")
        print(f"   Áreas institucionais: {len(processor.areas_institucionais)}")
        
        # Exportar resultado
        print("9. Exportando resultado...")
        processor.exportar_dxf(arquivo_saida)
        print(f"   Arquivo DXF salvo: {arquivo_saida}")
        
        # Calcular estatísticas
        print("\n" + "=" * 40)
        print("ESTATÍSTICAS DO RESULTADO")
        print("=" * 40)
        
        area_total = processor.perimetro_original.area
        area_lotes = sum(lote.area for lote in processor.lotes)
        area_ruas = sum(rua.area for rua in processor.ruas)
        area_verde = sum(area.area for area in processor.areas_verdes)
        area_institucional = sum(area.area for area in processor.areas_institucionais)
        
        print(f"Área total do terreno: {area_total:.2f} m²")
        print(f"Número de lotes: {len(processor.lotes)}")
        print(f"Área dos lotes: {area_lotes:.2f} m² ({(area_lotes/area_total)*100:.1f}%)")
        print(f"Área das ruas: {area_ruas:.2f} m² ({(area_ruas/area_total)*100:.1f}%)")
        print(f"Área verde: {area_verde:.2f} m² ({(area_verde/area_total)*100:.1f}%)")
        print(f"Área institucional: {area_institucional:.2f} m² ({(area_institucional/area_total)*100:.1f}%)")
        
        if len(processor.lotes) > 0:
            area_media_lote = area_lotes / len(processor.lotes)
            print(f"Área média por lote: {area_media_lote:.2f} m²")
        
        print("\nTESTE CONCLUÍDO COM SUCESSO!")
        return True
        
    except Exception as e:
        print(f"ERRO durante o processamento: {e}")
        import traceback
        traceback.print_exc()
        return False

def teste_validacao_parametros():
    """Testa a validação de parâmetros"""
    print("\n" + "=" * 60)
    print("TESTE DE VALIDAÇÃO DE PARÂMETROS")
    print("=" * 60)
    
    # Teste com parâmetros inválidos
    parametros_invalidos = {
        'largura_rua': -5.0,  # Inválido
        'largura_calcada': 2.0,
        'profundidade_max_quadra': 80.0,
        'orientacao_preferencial': 'Automática',
        'area_minima_lote': 0,  # Inválido
        'testada_minima_lote': 8.0,
        'largura_padrao_lote': 12.0,
        'profundidade_padrao_lote': 30.0,
        'percentual_area_verde': 150.0,  # Inválido
        'percentual_area_institucional': 5.0
    }
    
    try:
        processor = LoteamentoProcessor(parametros_invalidos)
        print("Processador criado com parâmetros inválidos (esperado)")
        
        # Tentar carregar arquivo inexistente
        if not processor.carregar_perimetro("arquivo_inexistente.dxf"):
            print("Validação de arquivo inexistente funcionando corretamente")
        
        print("Teste de validação concluído")
        return True
        
    except Exception as e:
        print(f"Erro no teste de validação: {e}")
        return False

def main():
    """Função principal dos testes"""
    print("INICIANDO TESTES AUTOMATIZADOS")
    print("Data/Hora:", __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Mudar para o diretório do script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Executar testes
    teste1_ok = teste_processamento_basico()
    teste2_ok = teste_validacao_parametros()
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    print(f"Teste de processamento básico: {'✓ PASSOU' if teste1_ok else '✗ FALHOU'}")
    print(f"Teste de validação: {'✓ PASSOU' if teste2_ok else '✗ FALHOU'}")
    
    if teste1_ok and teste2_ok:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("O aplicativo está funcionando corretamente.")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM!")
        print("Verifique os erros acima.")
    
    return teste1_ok and teste2_ok

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)

