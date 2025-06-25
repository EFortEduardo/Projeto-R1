import geopandas as gpd
import shapely
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import unary_union
import ezdxf
import numpy as np
import math
from typing import List, Tuple, Dict, Optional
import os

class LoteamentoProcessorMelhorado:
    """
    Versão melhorada do processador de loteamento com algoritmo de subdivisão aprimorado.
    """
    
    def __init__(self, parametros: Dict):
        """
        Inicializa o processador com os parâmetros fornecidos pela GUI.
        
        Args:
            parametros: Dicionário contendo todos os parâmetros do loteamento
        """
        self.parametros = parametros
        self.perimetro_original = None
        self.perimetro_internalizado = None
        self.malha_viaria = []
        self.quadras = []
        self.lotes = []
        self.areas_verdes = []
        self.areas_institucionais = []
        self.ruas = []
        
    def carregar_perimetro(self, arquivo_path: str) -> bool:
        """
        Carrega o perímetro do terreno a partir de arquivo DXF ou KML.
        
        Args:
            arquivo_path: Caminho para o arquivo de entrada
            
        Returns:
            True se carregado com sucesso, False caso contrário
        """
        try:
            extensao = os.path.splitext(arquivo_path)[1].lower()
            
            if extensao == '.kml':
                # Carregar arquivo KML usando GeoPandas
                gdf = gpd.read_file(arquivo_path)
                if len(gdf) > 0:
                    # Pegar a primeira geometria (assumindo que é o perímetro)
                    self.perimetro_original = gdf.geometry.iloc[0]
                    if isinstance(self.perimetro_original, MultiPolygon):
                        # Se for MultiPolygon, pegar o maior polígono
                        self.perimetro_original = max(self.perimetro_original.geoms, key=lambda x: x.area)
                else:
                    return False
                    
            elif extensao == '.dxf':
                # Carregar arquivo DXF usando ezdxf
                doc = ezdxf.readfile(arquivo_path)
                msp = doc.modelspace()
                
                # Procurar por polígonos ou polilinhas fechadas
                coordenadas = []
                
                for entity in msp:
                    if entity.dxftype() == 'LWPOLYLINE' and entity.closed:
                        # Polilinha fechada
                        pontos = [(p[0], p[1]) for p in entity.get_points()]
                        coordenadas = pontos
                        break
                    elif entity.dxftype() == 'POLYLINE' and entity.is_closed:
                        # Polilinha 3D fechada
                        pontos = [(v.dxf.location[0], v.dxf.location[1]) for v in entity.vertices]
                        coordenadas = pontos
                        break
                
                if coordenadas:
                    self.perimetro_original = Polygon(coordenadas)
                else:
                    return False
            else:
                return False
                
            # Verificar se o polígono é válido
            if not self.perimetro_original.is_valid:
                self.perimetro_original = self.perimetro_original.buffer(0)
                
            return True
            
        except Exception as e:
            print(f"Erro ao carregar perímetro: {e}")
            return False
    
    def internalizar_perimetro(self):
        """
        Aplica offset negativo ao perímetro para criar vias perimetrais.
        Etapa 1 do algoritmo.
        """
        # Calcular a distância do offset baseada na largura total da via
        largura_rua = self.parametros['largura_rua']
        largura_calcada = self.parametros['largura_calcada']
        offset_distance = (largura_rua + 2 * largura_calcada) / 2
        
        # Aplicar buffer negativo
        self.perimetro_internalizado = self.perimetro_original.buffer(-offset_distance)
        
        # Verificar se o resultado é válido
        if not self.perimetro_internalizado.is_valid or self.perimetro_internalizado.is_empty:
            # Se o offset for muito grande, reduzir progressivamente
            for reducao in [0.8, 0.6, 0.4, 0.2]:
                offset_distance_reduzido = offset_distance * reducao
                self.perimetro_internalizado = self.perimetro_original.buffer(-offset_distance_reduzido)
                if self.perimetro_internalizado.is_valid and not self.perimetro_internalizado.is_empty:
                    break
    
    def definir_eixo_principal(self) -> float:
        """
        Define o eixo principal do arruamento baseado na orientação natural do terreno.
        Etapa 2 do algoritmo.
        
        Returns:
            Ângulo do eixo principal em radianos
        """
        if self.parametros['orientacao_preferencial'] != 'Automática':
            # Usar orientação especificada pelo usuário
            orientacoes = {
                'Norte-Sul': 0,
                'Leste-Oeste': math.pi/2,
                'Nordeste-Sudoeste': math.pi/4,
                'Noroeste-Sudeste': 3*math.pi/4
            }
            return orientacoes.get(self.parametros['orientacao_preferencial'], 0)
        
        # Calcular retângulo de área mínima
        coords = list(self.perimetro_internalizado.exterior.coords)
        
        # Método simplificado: encontrar a direção do lado mais longo
        max_length = 0
        best_angle = 0
        
        for i in range(len(coords) - 1):
            p1 = coords[i]
            p2 = coords[i + 1]
            
            # Calcular comprimento e ângulo do segmento
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            length = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx)
            
            if length > max_length:
                max_length = length
                best_angle = angle
        
        return best_angle
    
    def subdividir_quadras_em_lotes_melhorado(self):
        """
        Versão melhorada da subdivisão de quadras em lotes.
        """
        area_minima = self.parametros['area_minima_lote']
        testada_minima = self.parametros['testada_minima_lote']
        largura_padrao = self.parametros['largura_padrao_lote']
        profundidade_padrao = self.parametros['profundidade_padrao_lote']
        
        for i, quadra in enumerate(self.quadras):
            if quadra.is_empty or quadra.area < area_minima * 2:  # Precisa de pelo menos 2 lotes
                continue
                
            print(f"Processando quadra {i+1}: área = {quadra.area:.2f} m²")
            
            # Encontrar o retângulo que melhor se ajusta à quadra
            bounds = quadra.bounds
            min_x, min_y, max_x, max_y = bounds
            
            largura_quadra = max_x - min_x
            altura_quadra = max_y - min_y
            
            # Determinar orientação dos lotes (frente para o lado mais longo)
            if largura_quadra >= altura_quadra:
                # Lotes com frente para o lado maior (horizontal)
                num_lotes_x = max(1, int(largura_quadra / largura_padrao))
                num_lotes_y = max(1, int(altura_quadra / profundidade_padrao))
                
                largura_lote = largura_quadra / num_lotes_x
                profundidade_lote = altura_quadra / num_lotes_y
                
                # Verificar se atende aos critérios mínimos
                if largura_lote < testada_minima:
                    num_lotes_x = max(1, int(largura_quadra / testada_minima))
                    largura_lote = largura_quadra / num_lotes_x
                
                area_lote = largura_lote * profundidade_lote
                if area_lote < area_minima:
                    # Ajustar número de lotes para atender área mínima
                    area_disponivel = largura_quadra * altura_quadra
                    num_lotes_max = int(area_disponivel / area_minima)
                    if num_lotes_max > 0:
                        num_lotes_x = min(num_lotes_x, num_lotes_max)
                        largura_lote = largura_quadra / num_lotes_x
                        profundidade_lote = altura_quadra
                        area_lote = largura_lote * profundidade_lote
                
                # Criar lotes
                for x in range(num_lotes_x):
                    for y in range(num_lotes_y):
                        x1 = min_x + x * largura_lote
                        y1 = min_y + y * profundidade_lote
                        x2 = x1 + largura_lote
                        y2 = y1 + profundidade_lote
                        
                        lote_coords = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
                        lote = Polygon(lote_coords)
                        
                        # Verificar se o lote está dentro da quadra
                        if lote.within(quadra.buffer(0.1)):  # Pequena tolerância
                            if lote.area >= area_minima and largura_lote >= testada_minima:
                                self.lotes.append(lote)
                                print(f"  Lote criado: {lote.area:.2f} m², testada: {largura_lote:.2f} m")
            
            else:
                # Lotes com frente para o lado menor (vertical)
                num_lotes_x = max(1, int(largura_quadra / profundidade_padrao))
                num_lotes_y = max(1, int(altura_quadra / largura_padrao))
                
                largura_lote = largura_quadra / num_lotes_x
                profundidade_lote = altura_quadra / num_lotes_y
                
                # Verificar se atende aos critérios mínimos
                if profundidade_lote < testada_minima:
                    num_lotes_y = max(1, int(altura_quadra / testada_minima))
                    profundidade_lote = altura_quadra / num_lotes_y
                
                area_lote = largura_lote * profundidade_lote
                if area_lote < area_minima:
                    # Ajustar número de lotes para atender área mínima
                    area_disponivel = largura_quadra * altura_quadra
                    num_lotes_max = int(area_disponivel / area_minima)
                    if num_lotes_max > 0:
                        num_lotes_y = min(num_lotes_y, num_lotes_max)
                        profundidade_lote = altura_quadra / num_lotes_y
                        largura_lote = largura_quadra
                        area_lote = largura_lote * profundidade_lote
                
                # Criar lotes
                for x in range(num_lotes_x):
                    for y in range(num_lotes_y):
                        x1 = min_x + x * largura_lote
                        y1 = min_y + y * profundidade_lote
                        x2 = x1 + largura_lote
                        y2 = y1 + profundidade_lote
                        
                        lote_coords = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
                        lote = Polygon(lote_coords)
                        
                        # Verificar se o lote está dentro da quadra
                        if lote.within(quadra.buffer(0.1)):  # Pequena tolerância
                            if lote.area >= area_minima and min(largura_lote, profundidade_lote) >= testada_minima:
                                self.lotes.append(lote)
                                print(f"  Lote criado: {lote.area:.2f} m², testada: {min(largura_lote, profundidade_lote):.2f} m")
    
    def criar_malha_viaria_simples(self):
        """
        Cria uma malha viária mais simples e eficaz.
        """
        bounds = self.perimetro_internalizado.bounds
        min_x, min_y, max_x, max_y = bounds
        
        largura_total = max_x - min_x
        altura_total = max_y - min_y
        profundidade_max = self.parametros['profundidade_max_quadra']
        
        # Criar linhas verticais (dividindo horizontalmente)
        num_linhas_verticais = max(1, int(largura_total / profundidade_max))
        for i in range(1, num_linhas_verticais):
            x = min_x + (i * largura_total / num_linhas_verticais)
            linha = LineString([(x, min_y - 10), (x, max_y + 10)])
            
            # Verificar intersecção com o perímetro
            intersecao = linha.intersection(self.perimetro_internalizado)
            if isinstance(intersecao, LineString) and intersecao.length > 0:
                self.malha_viaria.append(intersecao)
        
        # Criar linhas horizontais (dividindo verticalmente)
        num_linhas_horizontais = max(1, int(altura_total / profundidade_max))
        for i in range(1, num_linhas_horizontais):
            y = min_y + (i * altura_total / num_linhas_horizontais)
            linha = LineString([(min_x - 10, y), (max_x + 10, y)])
            
            # Verificar intersecção com o perímetro
            intersecao = linha.intersection(self.perimetro_internalizado)
            if isinstance(intersecao, LineString) and intersecao.length > 0:
                self.malha_viaria.append(intersecao)
    
    def dividir_em_quadras_simples(self):
        """
        Versão simplificada da divisão em quadras.
        """
        if not self.malha_viaria:
            # Se não há malha viária, usar o perímetro inteiro como uma quadra
            self.quadras = [self.perimetro_internalizado]
            return
        
        # Criar buffer das linhas da malha viária
        largura_rua = self.parametros['largura_rua']
        buffer_rua = largura_rua / 2
        
        # Unir todas as linhas da malha viária
        linhas_unidas = unary_union(self.malha_viaria)
        
        # Criar buffer das ruas
        ruas_buffer = linhas_unidas.buffer(buffer_rua)
        self.ruas = [ruas_buffer]
        
        # Subtrair as ruas do perímetro para obter as quadras
        area_quadras = self.perimetro_internalizado.difference(ruas_buffer)
        
        # Separar as quadras individuais
        if isinstance(area_quadras, MultiPolygon):
            self.quadras = [geom for geom in area_quadras.geoms if geom.area > 100]  # Filtrar quadras muito pequenas
        elif isinstance(area_quadras, Polygon) and not area_quadras.is_empty:
            self.quadras = [area_quadras]
    
    def alocar_areas_comuns(self):
        """
        Aloca áreas verdes e institucionais de forma mais inteligente.
        """
        area_total = self.perimetro_original.area
        percentual_verde = self.parametros['percentual_area_verde'] / 100
        percentual_institucional = self.parametros['percentual_area_institucional'] / 100
        
        area_verde_necessaria = area_total * percentual_verde
        area_institucional_necessaria = area_total * percentual_institucional
        
        # Usar quadras que não foram totalmente utilizadas para lotes
        area_verde_alocada = 0
        area_institucional_alocada = 0
        
        for quadra in self.quadras:
            # Verificar quantos lotes estão nesta quadra
            lotes_na_quadra = [lote for lote in self.lotes if lote.within(quadra.buffer(1.0))]
            area_lotes_quadra = sum(lote.area for lote in lotes_na_quadra)
            
            # Se a quadra tem pouco uso para lotes, usar para áreas comuns
            if area_lotes_quadra < quadra.area * 0.3:  # Menos de 30% utilizada
                if area_verde_alocada < area_verde_necessaria:
                    self.areas_verdes.append(quadra)
                    area_verde_alocada += quadra.area
                elif area_institucional_alocada < area_institucional_necessaria:
                    self.areas_institucionais.append(quadra)
                    area_institucional_alocada += quadra.area
    
    def exportar_dxf(self, arquivo_saida: str):
        """
        Exporta o resultado para arquivo DXF.
        """
        # Criar novo documento DXF
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        
        # Criar layers
        doc.layers.new('PERIMETRO', dxfattribs={'color': 1})  # Vermelho
        doc.layers.new('RUAS', dxfattribs={'color': 2})       # Amarelo
        doc.layers.new('QUADRAS', dxfattribs={'color': 3})    # Verde
        doc.layers.new('LOTES', dxfattribs={'color': 4})      # Ciano
        doc.layers.new('AREA_VERDE', dxfattribs={'color': 5}) # Azul
        doc.layers.new('AREA_INST', dxfattribs={'color': 6})  # Magenta
        
        # Adicionar perímetro original
        if self.perimetro_original:
            coords = list(self.perimetro_original.exterior.coords)
            msp.add_lwpolyline(coords, close=True, dxfattribs={'layer': 'PERIMETRO'})
        
        # Adicionar ruas
        for rua in self.ruas:
            if isinstance(rua, Polygon):
                coords = list(rua.exterior.coords)
                msp.add_lwpolyline(coords, close=True, dxfattribs={'layer': 'RUAS'})
        
        # Adicionar quadras
        for quadra in self.quadras:
            coords = list(quadra.exterior.coords)
            msp.add_lwpolyline(coords, close=True, dxfattribs={'layer': 'QUADRAS'})
        
        # Adicionar lotes
        for lote in self.lotes:
            coords = list(lote.exterior.coords)
            msp.add_lwpolyline(coords, close=True, dxfattribs={'layer': 'LOTES'})
        
        # Adicionar áreas verdes
        for area in self.areas_verdes:
            coords = list(area.exterior.coords)
            msp.add_lwpolyline(coords, close=True, dxfattribs={'layer': 'AREA_VERDE'})
        
        # Adicionar áreas institucionais
        for area in self.areas_institucionais:
            coords = list(area.exterior.coords)
            msp.add_lwpolyline(coords, close=True, dxfattribs={'layer': 'AREA_INST'})
        
        # Salvar arquivo
        doc.saveas(arquivo_saida)
    
    def processar_loteamento(self, arquivo_entrada: str, arquivo_saida: str) -> Dict:
        """
        Executa todo o processo de loteamento com algoritmo melhorado.
        """
        try:
            # Etapa 1: Carregar perímetro
            if not self.carregar_perimetro(arquivo_entrada):
                return {'sucesso': False, 'erro': 'Erro ao carregar perímetro'}
            
            # Etapa 2: Internalizar perímetro
            self.internalizar_perimetro()
            
            # Etapa 3: Criar malha viária simplificada
            self.criar_malha_viaria_simples()
            
            # Etapa 4: Dividir em quadras
            self.dividir_em_quadras_simples()
            
            # Etapa 5: Subdividir quadras em lotes (versão melhorada)
            self.subdividir_quadras_em_lotes_melhorado()
            
            # Etapa 6: Alocar áreas comuns
            self.alocar_areas_comuns()
            
            # Etapa 7: Exportar resultado
            self.exportar_dxf(arquivo_saida)
            
            # Calcular estatísticas
            area_total = self.perimetro_original.area
            num_lotes = len(self.lotes)
            area_lotes = sum(lote.area for lote in self.lotes)
            area_ruas = sum(rua.area for rua in self.ruas)
            area_verde = sum(area.area for area in self.areas_verdes)
            area_institucional = sum(area.area for area in self.areas_institucionais)
            
            estatisticas = {
                'sucesso': True,
                'area_total': area_total,
                'num_lotes': num_lotes,
                'area_lotes': area_lotes,
                'area_ruas': area_ruas,
                'area_verde': area_verde,
                'area_institucional': area_institucional,
                'percentual_lotes': (area_lotes / area_total) * 100,
                'percentual_ruas': (area_ruas / area_total) * 100,
                'percentual_verde': (area_verde / area_total) * 100,
                'percentual_institucional': (area_institucional / area_total) * 100
            }
            
            return estatisticas
            
        except Exception as e:
            return {'sucesso': False, 'erro': str(e)}

