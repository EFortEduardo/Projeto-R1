import geopandas as gpd
import shapely
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import unary_union
import ezdxf
import numpy as np
import math
from typing import List, Tuple, Dict, Optional
import os

class LoteamentoProcessorRobusto:
    """
    Versão robusta do processador de loteamento com tratamento completo de erros NaN.
    """
    
    def __init__(self, parametros: Dict):
        """
        Inicializa o processador com os parâmetros fornecidos pela GUI.
        
        Args:
            parametros: Dicionário contendo todos os parâmetros do loteamento
        """
        self.parametros = self._validar_e_limpar_parametros(parametros)
        self.perimetro_original = None
        self.perimetro_internalizado = None
        self.malha_viaria = []
        self.quadras = []
        self.lotes = []
        self.areas_verdes = []
        self.areas_institucionais = []
        self.ruas = []
        
    def _validar_e_limpar_parametros(self, parametros: Dict) -> Dict:
        """
        Valida e limpa os parâmetros, substituindo valores NaN por padrões seguros.
        
        Args:
            parametros: Parâmetros originais
            
        Returns:
            Parâmetros validados e limpos
        """
        parametros_limpos = {}
        
        # Valores padrão seguros
        padroes = {
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
        
        for chave, valor_padrao in padroes.items():
            valor = parametros.get(chave, valor_padrao)
            
            # Verificar se é string (orientação)
            if isinstance(valor_padrao, str):
                parametros_limpos[chave] = str(valor) if valor else valor_padrao
            else:
                # Verificar se é número válido
                try:
                    valor_float = float(valor)
                    if math.isnan(valor_float) or math.isinf(valor_float):
                        print(f"Aviso: Valor inválido para {chave}, usando padrão {valor_padrao}")
                        parametros_limpos[chave] = valor_padrao
                    else:
                        parametros_limpos[chave] = max(0.1, valor_float)  # Garantir valor positivo
                except (ValueError, TypeError):
                    print(f"Aviso: Valor não numérico para {chave}, usando padrão {valor_padrao}")
                    parametros_limpos[chave] = valor_padrao
        
        return parametros_limpos
    
    def _validar_numero(self, valor, nome_campo: str, minimo: float = 0.1, maximo: float = 1000.0) -> float:
        """
        Valida um número, garantindo que não seja NaN, infinito ou fora do intervalo.
        
        Args:
            valor: Valor a ser validado
            nome_campo: Nome do campo para mensagens de erro
            minimo: Valor mínimo permitido
            maximo: Valor máximo permitido
            
        Returns:
            Valor validado
        """
        try:
            valor_float = float(valor)
            if math.isnan(valor_float) or math.isinf(valor_float):
                raise ValueError(f"Valor inválido (NaN/Inf) para {nome_campo}")
            if valor_float < minimo:
                raise ValueError(f"Valor muito pequeno para {nome_campo}: {valor_float}")
            if valor_float > maximo:
                raise ValueError(f"Valor muito grande para {nome_campo}: {valor_float}")
            return valor_float
        except (ValueError, TypeError) as e:
            raise ValueError(f"Erro na validação de {nome_campo}: {e}")
    
    def carregar_perimetro(self, arquivo_path: str) -> bool:
        """
        Carrega o perímetro do terreno a partir de arquivo DXF ou KML.
        """
        try:
            print(f"Tentando carregar arquivo: {arquivo_path}")
            
            if not os.path.exists(arquivo_path):
                print(f"Arquivo não encontrado: {arquivo_path}")
                return False
                
            extensao = os.path.splitext(arquivo_path)[1].lower()
            print(f"Extensão detectada: {extensao}")
            
            if extensao == '.kml':
                print("Processando arquivo KML...")
                try:
                    gdf = gpd.read_file(arquivo_path)
                    print(f"GeoDataFrame carregado com {len(gdf)} geometrias")
                    
                    if len(gdf) > 0:
                        geometria = gdf.geometry.iloc[0]
                        print(f"Tipo de geometria: {type(geometria)}")
                        
                        if isinstance(geometria, MultiPolygon):
                            print("Convertendo MultiPolygon para Polygon")
                            self.perimetro_original = max(geometria.geoms, key=lambda x: x.area)
                        elif isinstance(geometria, Polygon):
                            self.perimetro_original = geometria
                        else:
                            print(f"Tipo de geometria não suportado: {type(geometria)}")
                            return False
                    else:
                        print("Nenhuma geometria encontrada no arquivo KML")
                        return False
                except Exception as e:
                    print(f"Erro ao processar KML: {e}")
                    return False
                    
            elif extensao == '.dxf':
                print("Processando arquivo DXF...")
                try:
                    doc = ezdxf.readfile(arquivo_path)
                    msp = doc.modelspace()
                    print("Arquivo DXF carregado com sucesso")
                    
                    coordenadas = []
                    entidades_encontradas = 0
                    
                    for entity in msp:
                        entidades_encontradas += 1
                        print(f"Entidade encontrada: {entity.dxftype()}")
                        
                        if entity.dxftype() == 'LWPOLYLINE':
                            print(f"LWPOLYLINE - Fechada: {entity.closed}")
                            if entity.closed:
                                pontos = [(p[0], p[1]) for p in entity.get_points()]
                                coordenadas = pontos
                                print(f"Coordenadas extraídas: {len(pontos)} pontos")
                                break
                        elif entity.dxftype() == 'POLYLINE':
                            print(f"POLYLINE - Fechada: {entity.is_closed}")
                            if entity.is_closed:
                                pontos = [(v.dxf.location[0], v.dxf.location[1]) for v in entity.vertices]
                                coordenadas = pontos
                                print(f"Coordenadas extraídas: {len(pontos)} pontos")
                                break
                    
                    print(f"Total de entidades processadas: {entidades_encontradas}")
                    
                    if coordenadas:
                        print(f"Validando {len(coordenadas)} coordenadas...")
                        # Validar coordenadas para NaN
                        coordenadas_validas = []
                        for i, (x, y) in enumerate(coordenadas):
                            if not (math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y)):
                                coordenadas_validas.append((x, y))
                            else:
                                print(f"Coordenada inválida no índice {i}: ({x}, {y})")
                        
                        print(f"Coordenadas válidas: {len(coordenadas_validas)}")
                        
                        if len(coordenadas_validas) >= 3:
                            self.perimetro_original = Polygon(coordenadas_validas)
                            print("Polígono criado com sucesso")
                        else:
                            print("Número insuficiente de coordenadas válidas")
                            return False
                    else:
                        print("Nenhuma polilinha fechada encontrada no arquivo DXF")
                        return False
                except Exception as e:
                    print(f"Erro ao processar DXF: {e}")
                    return False
            else:
                print(f"Extensão de arquivo não suportada: {extensao}")
                return False
                
            # Verificar se o polígono é válido e tem área positiva
            if not self.perimetro_original.is_valid:
                print("Polígono inválido, tentando corrigir...")
                self.perimetro_original = self.perimetro_original.buffer(0)
            
            if self.perimetro_original.area <= 0:
                print(f"Área do polígono inválida: {self.perimetro_original.area}")
                return False
                
            print(f"Perímetro carregado com sucesso. Área: {self.perimetro_original.area:.2f}")
            return True
            
        except Exception as e:
            print(f"Erro geral ao carregar perímetro: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def internalizar_perimetro(self):
        """
        Aplica offset negativo ao perímetro para criar vias perimetrais.
        """
        try:
            largura_rua = self._validar_numero(self.parametros['largura_rua'], 'largura_rua', 0.1, 100.0)
            largura_calcada = self._validar_numero(self.parametros['largura_calcada'], 'largura_calcada', 0.0, 50.0)
            
            offset_distance = (largura_rua + 2 * largura_calcada) / 2
            offset_distance = self._validar_numero(offset_distance, 'offset_distance', 0.1, 200.0)
            
            # Aplicar buffer negativo
            self.perimetro_internalizado = self.perimetro_original.buffer(-offset_distance)
            
            # Verificar se o resultado é válido
            if not self.perimetro_internalizado.is_valid or self.perimetro_internalizado.is_empty:
                # Reduzir progressivamente o offset
                for reducao in [0.8, 0.6, 0.4, 0.2, 0.1]:
                    offset_reduzido = offset_distance * reducao
                    self.perimetro_internalizado = self.perimetro_original.buffer(-offset_reduzido)
                    if (self.perimetro_internalizado.is_valid and 
                        not self.perimetro_internalizado.is_empty and 
                        self.perimetro_internalizado.area > 0):
                        break
                        
            # Se ainda não é válido, usar o perímetro original
            if (not self.perimetro_internalizado.is_valid or 
                self.perimetro_internalizado.is_empty or 
                self.perimetro_internalizado.area <= 0):
                self.perimetro_internalizado = self.perimetro_original
                
        except Exception as e:
            print(f"Erro na internalização: {e}")
            self.perimetro_internalizado = self.perimetro_original
    
    def criar_malha_viaria_robusta(self):
        """
        Cria uma malha viária com validação robusta contra NaN.
        """
        try:
            bounds = self.perimetro_internalizado.bounds
            min_x, min_y, max_x, max_y = bounds
            
            # Validar bounds
            for coord in bounds:
                if math.isnan(coord) or math.isinf(coord):
                    raise ValueError("Coordenadas inválidas no perímetro")
            
            largura_total = self._validar_numero(max_x - min_x, 'largura_total', 1.0, 10000.0)
            altura_total = self._validar_numero(max_y - min_y, 'altura_total', 1.0, 10000.0)
            profundidade_max = self._validar_numero(self.parametros['profundidade_max_quadra'], 'profundidade_max', 10.0, 1000.0)
            
            # Calcular número de linhas de forma segura
            num_linhas_verticais = max(1, int(largura_total / profundidade_max))
            num_linhas_horizontais = max(1, int(altura_total / profundidade_max))
            
            # Limitar número de linhas para evitar processamento excessivo
            num_linhas_verticais = min(num_linhas_verticais, 10)
            num_linhas_horizontais = min(num_linhas_horizontais, 10)
            
            # Criar linhas verticais
            if num_linhas_verticais > 1:
                for i in range(1, num_linhas_verticais):
                    x = min_x + (i * largura_total / num_linhas_verticais)
                    if not (math.isnan(x) or math.isinf(x)):
                        linha = LineString([(x, min_y - 10), (x, max_y + 10)])
                        intersecao = linha.intersection(self.perimetro_internalizado)
                        if isinstance(intersecao, LineString) and intersecao.length > 0:
                            self.malha_viaria.append(intersecao)
            
            # Criar linhas horizontais
            if num_linhas_horizontais > 1:
                for i in range(1, num_linhas_horizontais):
                    y = min_y + (i * altura_total / num_linhas_horizontais)
                    if not (math.isnan(y) or math.isinf(y)):
                        linha = LineString([(min_x - 10, y), (max_x + 10, y)])
                        intersecao = linha.intersection(self.perimetro_internalizado)
                        if isinstance(intersecao, LineString) and intersecao.length > 0:
                            self.malha_viaria.append(intersecao)
                            
        except Exception as e:
            print(f"Erro na criação da malha viária: {e}")
            self.malha_viaria = []
    
    def dividir_em_quadras_robusta(self):
        """
        Versão robusta da divisão em quadras.
        """
        try:
            if not self.malha_viaria:
                self.quadras = [self.perimetro_internalizado]
                return
            
            largura_rua = self._validar_numero(self.parametros['largura_rua'], 'largura_rua', 0.1, 100.0)
            buffer_rua = largura_rua / 2
            
            linhas_unidas = unary_union(self.malha_viaria)
            ruas_buffer = linhas_unidas.buffer(buffer_rua)
            self.ruas = [ruas_buffer]
            
            area_quadras = self.perimetro_internalizado.difference(ruas_buffer)
            
            if isinstance(area_quadras, MultiPolygon):
                self.quadras = [geom for geom in area_quadras.geoms 
                              if geom.area > 100 and geom.is_valid]
            elif isinstance(area_quadras, Polygon) and not area_quadras.is_empty and area_quadras.area > 100:
                self.quadras = [area_quadras]
            else:
                self.quadras = [self.perimetro_internalizado]
                
        except Exception as e:
            print(f"Erro na divisão em quadras: {e}")
            self.quadras = [self.perimetro_internalizado]
    
    def subdividir_quadras_robusta(self):
        """
        Versão robusta da subdivisão de quadras em lotes.
        """
        try:
            area_minima = self._validar_numero(self.parametros['area_minima_lote'], 'area_minima_lote', 50.0, 10000.0)
            testada_minima = self._validar_numero(self.parametros['testada_minima_lote'], 'testada_minima_lote', 3.0, 200.0)
            largura_padrao = self._validar_numero(self.parametros['largura_padrao_lote'], 'largura_padrao_lote', 5.0, 200.0)
            profundidade_padrao = self._validar_numero(self.parametros['profundidade_padrao_lote'], 'profundidade_padrao_lote', 10.0, 500.0)
            
            for i, quadra in enumerate(self.quadras):
                if quadra.is_empty or quadra.area < area_minima * 2:
                    continue
                    
                try:
                    bounds = quadra.bounds
                    min_x, min_y, max_x, max_y = bounds
                    
                    # Validar bounds da quadra
                    for coord in bounds:
                        if math.isnan(coord) or math.isinf(coord):
                            continue
                    
                    largura_quadra = self._validar_numero(max_x - min_x, f'largura_quadra_{i}', 1.0, 10000.0)
                    altura_quadra = self._validar_numero(max_y - min_y, f'altura_quadra_{i}', 1.0, 10000.0)
                    
                    # Calcular número de lotes de forma segura
                    num_lotes_x = max(1, int(largura_quadra / largura_padrao))
                    num_lotes_y = max(1, int(altura_quadra / profundidade_padrao))
                    
                    # Limitar número de lotes
                    num_lotes_x = min(num_lotes_x, 20)
                    num_lotes_y = min(num_lotes_y, 20)
                    
                    largura_lote = largura_quadra / num_lotes_x
                    profundidade_lote = altura_quadra / num_lotes_y
                    
                    # Validar dimensões dos lotes
                    largura_lote = self._validar_numero(largura_lote, f'largura_lote_{i}', 1.0, 500.0)
                    profundidade_lote = self._validar_numero(profundidade_lote, f'profundidade_lote_{i}', 1.0, 500.0)
                    
                    # Verificar se atende aos critérios mínimos
                    if largura_lote < testada_minima:
                        num_lotes_x = max(1, int(largura_quadra / testada_minima))
                        largura_lote = largura_quadra / num_lotes_x
                    
                    area_lote = largura_lote * profundidade_lote
                    if area_lote < area_minima:
                        area_disponivel = largura_quadra * altura_quadra
                        num_lotes_max = max(1, int(area_disponivel / area_minima))
                        num_lotes_x = min(num_lotes_x, num_lotes_max)
                        if num_lotes_x > 0:
                            largura_lote = largura_quadra / num_lotes_x
                    
                    # Criar lotes
                    for x in range(num_lotes_x):
                        for y in range(num_lotes_y):
                            try:
                                x1 = min_x + x * largura_lote
                                y1 = min_y + y * profundidade_lote
                                x2 = x1 + largura_lote
                                y2 = y1 + profundidade_lote
                                
                                # Validar coordenadas do lote
                                coords = [x1, y1, x2, y2]
                                if any(math.isnan(c) or math.isinf(c) for c in coords):
                                    continue
                                
                                lote_coords = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
                                lote = Polygon(lote_coords)
                                
                                if (lote.is_valid and 
                                    lote.within(quadra.buffer(0.1)) and 
                                    lote.area >= area_minima and 
                                    min(largura_lote, profundidade_lote) >= testada_minima):
                                    self.lotes.append(lote)
                                    
                            except Exception as e_lote:
                                print(f"Erro ao criar lote {x},{y} na quadra {i}: {e_lote}")
                                continue
                                
                except Exception as e_quadra:
                    print(f"Erro ao processar quadra {i}: {e_quadra}")
                    continue
                    
        except Exception as e:
            print(f"Erro na subdivisão de quadras: {e}")
    
    def alocar_areas_comuns_robusta(self):
        """
        Versão robusta da alocação de áreas comuns.
        """
        try:
            area_total = self._validar_numero(self.perimetro_original.area, 'area_total', 100.0, 1000000.0)
            percentual_verde = self._validar_numero(self.parametros['percentual_area_verde'], 'percentual_verde', 0, 100) / 100
            percentual_institucional = self._validar_numero(self.parametros['percentual_area_institucional'], 'percentual_institucional', 0, 100) / 100
            
            # Limitar percentuais
            percentual_verde = min(percentual_verde, 0.5)  # Máximo 50%
            percentual_institucional = min(percentual_institucional, 0.3)  # Máximo 30%
            
            area_verde_necessaria = area_total * percentual_verde
            area_institucional_necessaria = area_total * percentual_institucional
            
            area_verde_alocada = 0
            area_institucional_alocada = 0
            
            for quadra in self.quadras:
                try:
                    if quadra.area <= 0:
                        continue
                        
                    lotes_na_quadra = [lote for lote in self.lotes 
                                     if lote.within(quadra.buffer(1.0))]
                    area_lotes_quadra = sum(lote.area for lote in lotes_na_quadra)
                    
                    if area_lotes_quadra < quadra.area * 0.3:
                        if area_verde_alocada < area_verde_necessaria:
                            self.areas_verdes.append(quadra)
                            area_verde_alocada += quadra.area
                        elif area_institucional_alocada < area_institucional_necessaria:
                            self.areas_institucionais.append(quadra)
                            area_institucional_alocada += quadra.area
                            
                except Exception as e_area:
                    print(f"Erro ao alocar área comum: {e_area}")
                    continue
                    
        except Exception as e:
            print(f"Erro na alocação de áreas comuns: {e}")
    
    def exportar_dxf_robusto(self, arquivo_saida: str):
        """
        Versão robusta da exportação DXF.
        """
        try:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            # Criar layers
            doc.layers.new('PERIMETRO', dxfattribs={'color': 1})
            doc.layers.new('RUAS', dxfattribs={'color': 2})
            doc.layers.new('QUADRAS', dxfattribs={'color': 3})
            doc.layers.new('LOTES', dxfattribs={'color': 4})
            doc.layers.new('AREA_VERDE', dxfattribs={'color': 5})
            doc.layers.new('AREA_INST', dxfattribs={'color': 6})
            
            # Função auxiliar para validar coordenadas
            def coords_validas(coords):
                return [(x, y) for x, y in coords 
                       if not (math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y))]
            
            # Adicionar perímetro original
            if self.perimetro_original:
                coords = coords_validas(self.perimetro_original.exterior.coords)
                if len(coords) >= 3:
                    msp.add_lwpolyline(coords, close=True, dxfattribs={'layer': 'PERIMETRO'})
            
            # Adicionar ruas
            for rua in self.ruas:
                if isinstance(rua, Polygon):
                    coords = coords_validas(rua.exterior.coords)
                    if len(coords) >= 3:
                        msp.add_lwpolyline(coords, close=True, dxfattribs={'layer': 'RUAS'})
            
            # Adicionar quadras
            for quadra in self.quadras:
                coords = coords_validas(quadra.exterior.coords)
                if len(coords) >= 3:
                    msp.add_lwpolyline(coords, close=True, dxfattribs={'layer': 'QUADRAS'})
            
            # Adicionar lotes
            for lote in self.lotes:
                coords = coords_validas(lote.exterior.coords)
                if len(coords) >= 3:
                    msp.add_lwpolyline(coords, close=True, dxfattribs={'layer': 'LOTES'})
            
            # Adicionar áreas verdes
            for area in self.areas_verdes:
                coords = coords_validas(area.exterior.coords)
                if len(coords) >= 3:
                    msp.add_lwpolyline(coords, close=True, dxfattribs={'layer': 'AREA_VERDE'})
            
            # Adicionar áreas institucionais
            for area in self.areas_institucionais:
                coords = coords_validas(area.exterior.coords)
                if len(coords) >= 3:
                    msp.add_lwpolyline(coords, close=True, dxfattribs={'layer': 'AREA_INST'})
            
            doc.saveas(arquivo_saida)
            
        except Exception as e:
            print(f"Erro na exportação DXF: {e}")
            raise
    
    def processar_loteamento_robusto(self, arquivo_entrada: str, arquivo_saida: str) -> Dict:
        """
        Executa todo o processo de loteamento com tratamento robusto de erros.
        """
        try:
            # Etapa 1: Carregar perímetro
            if not self.carregar_perimetro(arquivo_entrada):
                return {'sucesso': False, 'erro': 'Erro ao carregar perímetro'}
            
            # Etapa 2: Internalizar perímetro
            self.internalizar_perimetro()
            
            # Etapa 3: Criar malha viária
            self.criar_malha_viaria_robusta()
            
            # Etapa 4: Dividir em quadras
            self.dividir_em_quadras_robusta()
            
            # Etapa 5: Subdividir quadras em lotes
            self.subdividir_quadras_robusta()
            
            # Etapa 6: Alocar áreas comuns
            self.alocar_areas_comuns_robusta()
            
            # Etapa 7: Exportar resultado
            self.exportar_dxf_robusto(arquivo_saida)
            
            # Calcular estatísticas com validação
            area_total = self._validar_numero(self.perimetro_original.area, 'area_total_final', 100.0, 1000000.0)
            num_lotes = len(self.lotes)
            area_lotes = sum(lote.area for lote in self.lotes if lote.area > 0)
            area_ruas = sum(rua.area for rua in self.ruas if rua.area > 0)
            area_verde = sum(area.area for area in self.areas_verdes if area.area > 0)
            area_institucional = sum(area.area for area in self.areas_institucionais if area.area > 0)
            
            estatisticas = {
                'sucesso': True,
                'area_total': area_total,
                'num_lotes': num_lotes,
                'area_lotes': area_lotes,
                'area_ruas': area_ruas,
                'area_verde': area_verde,
                'area_institucional': area_institucional,
                'percentual_lotes': (area_lotes / area_total) * 100 if area_total > 0 else 0,
                'percentual_ruas': (area_ruas / area_total) * 100 if area_total > 0 else 0,
                'percentual_verde': (area_verde / area_total) * 100 if area_total > 0 else 0,
                'percentual_institucional': (area_institucional / area_total) * 100 if area_total > 0 else 0
            }
            
            return estatisticas
            
        except Exception as e:
            return {'sucesso': False, 'erro': f'Erro no processamento: {str(e)}'}

