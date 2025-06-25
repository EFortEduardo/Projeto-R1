#!/usr/bin/env python3
"""
Script de teste abrangente para o LoteamentoProcessorUltraAvancado e a GUI.
Verifica as novas funcionalidades de: 
- Parâmetros de lotes (min/max área, testada, profundidade)
- Subdivisão de lotes irregulares
- Distribuição de lotes de esquina
- Liberdade criativa na formação de quadras
- Alocação de áreas comuns
- Acesso aos lotes
"""

import os
import sys
import subprocess
import time
import ezdxf
from shapely.geometry import Polygon

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from loteamento_processor_ultra_avancado import LoteamentoProcessorUltraAvancado

OUTPUT_DIR = "output"
TEST_DXF_DIR = "test_dxf"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

if not os.path.exists(TEST_DXF_DIR):
    os.makedirs(TEST_DXF_DIR)

def create_test_dxf(filename, points):
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    msp.add_lwpolyline(points, close=True)
    doc.saveas(os.path.join(TEST_DXF_DIR, filename))
    print(f"Created test DXF: {filename}")

def run_processor_test(test_name, params, input_dxf, expected_min_lotes=1, expected_max_lotes=100):
    print(f"\n--- Running Test: {test_name} ---")
    processor = LoteamentoProcessorUltraAvancado(params)
    output_dxf = os.path.join(OUTPUT_DIR, f"{test_name}_resultado.dxf")
    
    result = processor.processar_loteamento_ultra_avancado(os.path.join(TEST_DXF_DIR, input_dxf), output_dxf)
    
    if result["sucesso"]:
        print(f"Test \'{test_name}\' SUCCEEDED.")
        area_lotes_perc = (result["area_lotes"]/result["area_total"])*100
        area_ruas_perc = (result["area_ruas"]/result["area_total"])*100
        area_calcadas_perc = (result["area_calcadas"]/result["area_total"])*100
        area_verde_perc = (result["area_verde"]/result["area_total"])*100
        area_institucional_perc = (result["area_institucional"]/result["area_total"])*100

        print(f'  Total Area: {result["area_total"]:.2f} m²')
        print(f'  Number of Lots: {result["num_lotes"]}')
        print(f'  Lot Area: {result["area_lotes"]:.2f} m² ({area_lotes_perc:.1f}%)')
        print(f'  Road Area: {result["area_ruas"]:.2f} m² ({area_ruas_perc:.1f}%)')
        print(f'  Sidewalk Area: {result["area_calcadas"]:.2f} m² ({area_calcadas_perc:.1f}%)')
        print(f'  Green Area: {result["area_verde"]:.2f} m² ({area_verde_perc:.1f}%)')
        print(f'  Institutional Area: {result["area_institucional"]:.2f} m² ({area_institucional_perc:.1f}%)')
        
        num_lotes_actual = result["num_lotes"]
        assert num_lotes_actual >= expected_min_lotes, f"Expected at least {expected_min_lotes} lots, got {num_lotes_actual}"
        assert num_lotes_actual <= expected_max_lotes, f"Expected at most {expected_max_lotes} lots, got {num_lotes_actual}"
        assert os.path.exists(output_dxf), f"Output DXF {output_dxf} not found."
        
        # Basic check for lot access (more detailed check would require geometry analysis)
        # For now, just ensure some lots were created
        assert result["area_lotes"] > 0, "No lots created or lot area is zero."
        
        print(f"Test \'{test_name}\' PASSED.\n")
        return True
    else:
        print(f"Test \'{test_name}\' FAILED: {result['erro']}\n")
        return False

def main():
    # Create test DXF files
    create_test_dxf("retangular.dxf", [(0,0), (100,0), (100,200), (0,200)])
    create_test_dxf("irregular1.dxf", [(0,0), (120,10), (100,200), (20,190), (0,0)])
    create_test_dxf("irregular2.dxf", [(0,0), (150, -20), (200, 100), (100, 250), (0, 200), (-50, 50), (0,0)])

    all_tests_passed = True

    # Test Case 1: Default parameters, rectangular area
    params1 = {
        'largura_rua': 8.0,
        'largura_calcada': 2.0,
        'profundidade_max_quadra': 60.0,
        'orientacao_preferencial': 'Automática',
        'area_minima_lote': 200.0,
        'area_maxima_lote': 600.0,
        'area_preferencial_lote': 300.0,
        'testada_minima_lote': 8.0,
        'testada_maxima_lote': 20.0,
        'testada_preferencial_lote': 12.0,
        'profundidade_minima_lote': 15.0,
        'profundidade_maxima_lote': 40.0,
        'profundidade_padrao_lote': 25.0,
        'percentual_area_verde': 15.0,
        'percentual_area_institucional': 5.0,
        'prioridade_aproveitamento': 'Máximo Aproveitamento',
        'tolerancia_forma': 'Alta (Mais Irregular)',
        'estrategia_esquina': 'Automático',
        'densidade_lotes': 'Alta',
        'liberdade_criativa': 'Máxima',
        'experimentacao_formas': 'Totalmente Livres'
    }
    if not run_processor_test("Default_Rectangular", params1, "retangular.dxf", expected_min_lotes=17, expected_max_lotes=50):
        all_tests_passed = False

    # Test Case 2: Irregular area, focus on regular lots
    params2 = params1.copy()
    params2["tolerancia_forma"] = "Baixa (Mais Regular)"
    params2["experimentacao_formas"] = "Retangulares"
    if not run_processor_test("Regular_Irregular1", params2, "irregular1.dxf", expected_min_lotes=10, expected_max_lotes=34):
        all_tests_passed = False

    # Test Case 3: Irregular area, focus on irregular lots and corner strategy
    params3 = params1.copy()
    params3["tolerancia_forma"] = "Alta (Mais Irregular)"
    params3["estrategia_esquina"] = "Testada Maior"
    params3["liberdade_criativa"] = "Criativa"
    if not run_processor_test("Irregular_Corner_Creative", params3, "irregular2.dxf", expected_min_lotes=15, expected_max_lotes=43):
        all_tests_passed = False

    # Test Case 4: Larger lots, lower density
    params4 = params1.copy()
    params4["area_minima_lote"] = 400.0
    params4["area_maxima_lote"] = 1000.0
    params4["densidade_lotes"] = "Baixa"
    if not run_processor_test("LargerLots_LowerDensity", params4, "retangular.dxf", expected_min_lotes=5, expected_max_lotes=20):
        all_tests_passed = False

    # Test Case 5: Smaller lots, higher density
    params5 = params1.copy()
    params5["area_minima_lote"] = 100.0
    params5["area_maxima_lote"] = 300.0
    params5["densidade_lotes"] = "Máxima"
    if not run_processor_test("SmallerLots_HigherDensity", params5, "retangular.dxf", expected_min_lotes=25, expected_max_lotes=100):
        all_tests_passed = False

    # Test Case 6: Specific road and sidewalk width
    params6 = params1.copy()
    params6["largura_rua"] = 10.0
    params6["largura_calcada"] = 3.0
    if not run_processor_test("CustomRoadSidewalk", params6, "retangular.dxf", expected_min_lotes=19, expected_max_lotes=50):
        all_tests_passed = False

    # Test Case 7: Different common area percentages
    params7 = params1.copy()
    params7["percentual_area_verde"] = 20.0
    params7["percentual_area_institucional"] = 10.0
    if not run_processor_test("CustomCommonAreas", params7, "retangular.dxf", expected_min_lotes=15, expected_max_lotes=40):
        all_tests_passed = False

    if all_tests_passed:
        print("\nALL TESTS PASSED SUCCESSFULLY!")
    else:
        print("\nSOME TESTS FAILED. Please check the logs above.")

if __name__ == "__main__":
    main()


