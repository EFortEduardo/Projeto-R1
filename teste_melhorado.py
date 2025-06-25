#!/usr/bin/env python3
"""
Teste do processador melhorado
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from loteamento_processor_melhorado import LoteamentoProcessorMelhorado

def teste_processador_melhorado():
    """Testa o processador melhorado"""
    print("=" * 60)
    print("TESTE DO PROCESSADOR MELHORADO")
    print("=" * 60)
    
    # Parâmetros de teste
    parametros = {
        'largura_rua': 8.0,
        'largura_calcada': 2.0,
        'profundidade_max_quadra': 40.0,  # Reduzido para criar mais quadras
        'orientacao_preferencial': 'Automática',
        'area_minima_lote': 200.0,
        'testada_minima_lote': 8.0,
        'largura_padrao_lote': 12.0,
        'profundidade_padrao_lote': 25.0,  # Reduzido para caber mais lotes
        'percentual_area_verde': 15.0,
        'percentual_area_institucional': 5.0
    }
    
    # Arquivos
    arquivo_entrada = os.path.join("assets", "perimetro_retangular.dxf")
    arquivo_saida = os.path.join("output", "teste_melhorado_resultado.dxf")
    
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
        # Criar processador melhorado
        print("1. Criando processador melhorado...")
        processor = LoteamentoProcessorMelhorado(parametros)
        
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
        
        # Criar malha viária
        print("4. Criando malha viária...")
        processor.criar_malha_viaria_simples()
        print(f"   Malha viária criada. Linhas: {len(processor.malha_viaria)}")
        
        # Dividir em quadras
        print("5. Dividindo em quadras...")
        processor.dividir_em_quadras_simples()
        print(f"   Quadras criadas: {len(processor.quadras)}")
        for i, quadra in enumerate(processor.quadras):
            print(f"     Quadra {i+1}: {quadra.area:.2f} m²")
        
        # Subdividir em lotes
        print("6. Subdividindo quadras em lotes...")
        processor.subdividir_quadras_em_lotes_melhorado()
        print(f"   Lotes criados: {len(processor.lotes)}")
        
        # Alocar áreas comuns
        print("7. Alocando áreas comuns...")
        processor.alocar_areas_comuns()
        print(f"   Áreas verdes: {len(processor.areas_verdes)}")
        print(f"   Áreas institucionais: {len(processor.areas_institucionais)}")
        
        # Exportar resultado
        print("8. Exportando resultado...")
        processor.exportar_dxf(arquivo_saida)
        print(f"   Arquivo DXF salvo: {arquivo_saida}")
        
        # Calcular estatísticas
        print("\n" + "=" * 40)
        print("ESTATÍSTICAS DO RESULTADO MELHORADO")
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
            
            # Estatísticas dos lotes
            areas_lotes = [lote.area for lote in processor.lotes]
            print(f"Menor lote: {min(areas_lotes):.2f} m²")
            print(f"Maior lote: {max(areas_lotes):.2f} m²")
        
        print("\nTESTE DO PROCESSADOR MELHORADO CONCLUÍDO COM SUCESSO!")
        return True
        
    except Exception as e:
        print(f"ERRO durante o processamento: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal dos testes"""
    print("INICIANDO TESTE DO PROCESSADOR MELHORADO")
    print("Data/Hora:", __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Mudar para o diretório do script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Executar teste
    sucesso = teste_processador_melhorado()
    
    if sucesso:
        print("\n🎉 TESTE PASSOU!")
        print("O processador melhorado está funcionando corretamente.")
    else:
        print("\n❌ TESTE FALHOU!")
        print("Verifique os erros acima.")
    
    return sucesso

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)

