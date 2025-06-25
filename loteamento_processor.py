import geopandas as gpd
import shapely
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import unary_union
import ezdxf
import numpy as np
import math
from typing import List, Tuple, Dict, Optional
import os

class LoteamentoProcessor:
    """
    Classe responsável pelo processamento geoespacial e algoritmo de loteamento.
    Implementa todas as etapas descritas no plano de desenvolvimento.
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
            # Se o offset for muito grande, reduzir
            offset_distance = offset_distance * 0.8
            self.perimetro_internalizado = self.perimetro_original.buffer(-offset_distance)
    
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
    
    def criar_malha_viaria(self, eixo_principal: float):
        """
        Cria a malha viária principal baseada no eixo principal.
        Etapa 3 do algoritmo.
        
        Args:
            eixo_principal: Ângulo do eixo principal em radianos
        """
        bounds = self.perimetro_internalizado.bounds
        min_x, min_y, max_x, max_y = bounds
        
        profundidade_max = self.parametros['profundidade_max_quadra']
        
        # Criar linhas paralelas ao eixo principal
        cos_angle = math.cos(eixo_principal)
        sin_angle = math.sin(eixo_principal)
        
        # Calcular dimensões rotacionadas
        width = max_x - min_x
        height = max_y - min_y
        
        # Número de linhas baseado na profundidade máxima
        num_linhas_paralelas = int(max(width, height) / profundidade_max) + 1
        num_linhas_perpendiculares = int(min(width, height) / profundidade_max) + 1
        
        # Criar linhas paralelas
        for i in range(num_linhas_paralelas + 1):
            offset = i * profundidade_max
            
            # Linha na direção do eixo principal
            start_x = min_x + offset * cos_angle
            start_y = min_y + offset * sin_angle
            end_x = start_x + height * (-sin_angle)
            end_y = start_y + height * cos_angle
            
            linha = LineString([(start_x, start_y), (end_x, end_y)])
            
            # Verificar se a linha intersecta o perímetro
            if linha.intersects(self.perimetro_internalizado):
                intersecao = linha.intersection(self.perimetro_internalizado)
                if isinstance(intersecao, LineString):
                    self.malha_viaria.append(intersecao)
        
        # Criar linhas perpendiculares
        for i in range(num_linhas_perpendiculares + 1):
            offset = i * profundidade_max
            
            # Linha perpendicular ao eixo principal
            start_x = min_x + offset * (-sin_angle)
            start_y = min_y + offset * cos_angle
            end_x = start_x + width * cos_angle
            end_y = start_y + width * sin_angle
            
            linha = LineString([(start_x, start_y), (end_x, end_y)])
            
            # Verificar se a linha intersecta o perímetro
            if linha.intersects(self.perimetro_internalizado):
                intersecao = linha.intersection(self.perimetro_internalizado)
                if isinstance(intersecao, LineString):
                    self.malha_viaria.append(intersecao)
    
    def dividir_em_quadras(self):
        """
        Divide o perímetro em quadras usando a malha viária.
        Etapa 4 do algoritmo.
        """
        # Criar buffer das linhas da malha viária para "cortar" o polígono
        largura_rua = self.parametros['largura_rua']
        buffer_rua = largura_rua / 2
        
        # Unir todas as linhas da malha viária
        if self.malha_viaria:
            linhas_unidas = unary_union(self.malha_viaria)
            
            # Criar buffer das ruas
            ruas_buffer = linhas_unidas.buffer(buffer_rua)
            
            # Subtrair as ruas do perímetro para obter as quadras
            area_quadras = self.perimetro_internalizado.difference(ruas_buffer)
            
            # Armazenar as ruas
            self.ruas = [ruas_buffer]
            
            # Separar as quadras individuais
            if isinstance(area_quadras, MultiPolygon):
                self.quadras = list(area_quadras.geoms)
            elif isinstance(area_quadras, Polygon) and not area_quadras.is_empty:
                self.quadras = [area_quadras]
        else:
            # Se não há malha viária, usar o perímetro inteiro como uma quadra
            self.quadras = [self.perimetro_internalizado]
    
    def subdividir_quadras_em_lotes(self):
        """
        Subdivide cada quadra em lotes individuais.
        Etapa 5 do algoritmo.
        """
        area_minima = self.parametros['area_minima_lote']
        testada_minima = self.parametros['testada_minima_lote']
        largura_padrao = self.parametros['largura_padrao_lote']
        profundidade_padrao = self.parametros['profundidade_padrao_lote']
        
        for quadra in self.quadras:
            if quadra.is_empty or quadra.area < area_minima:
                continue
                
            # Aplicar offset negativo para criar espaço frontal dos lotes
            offset_lote = 2.0  # 2 metros de recuo
            quadra_interna = quadra.buffer(-offset_lote)
            
            if quadra_interna.is_empty:
                continue
            
            # Encontrar o lado mais longo da quadra (frente)
            coords = list(quadra.exterior.coords)
            max_length = 0
            melhor_lado = None
            
            for i in range(len(coords) - 1):
                p1 = coords[i]
                p2 = coords[i + 1]
                length = Point(p1).distance(Point(p2))
                
                if length > max_length:
                    max_length = length
                    melhor_lado = LineString([p1, p2])
            
            if melhor_lado is None:
                continue
            
            # Dividir a frente em lotes
            num_lotes = max(1, int(max_length / largura_padrao))
            largura_real = max_length / num_lotes
            
            # Verificar se a largura real atende à testada mínima
            if largura_real < testada_minima:
                num_lotes = max(1, int(max_length / testada_minima))
                largura_real = max_length / num_lotes
            
            # Criar lotes ao longo da frente
            for i in range(num_lotes):
                # Calcular posição do lote na frente
                t_start = i / num_lotes
                t_end = (i + 1) / num_lotes
                
                # Pontos na frente do lote
                p_start = melhor_lado.interpolate(t_start, normalized=True)
                p_end = melhor_lado.interpolate(t_end, normalized=True)
                
                # Criar retângulo do lote (simplificado)
                # Calcular direção perpendicular à frente
                dx = p_end.x - p_start.x
                dy = p_end.y - p_start.y
                length = math.sqrt(dx*dx + dy*dy)
                
                if length > 0:
                    # Vetor unitário perpendicular
                    perp_x = -dy / length
                    perp_y = dx / length
                    
                    # Pontos do fundo do lote
                    prof_real = min(profundidade_padrao, quadra_interna.bounds[3] - quadra_interna.bounds[1])
                    p_back_start = Point(p_start.x + perp_x * prof_real, p_start.y + perp_y * prof_real)
                    p_back_end = Point(p_end.x + perp_x * prof_real, p_end.y + perp_y * prof_real)
                    
                    # Criar polígono do lote
                    lote_coords = [
                        (p_start.x, p_start.y),
                        (p_end.x, p_end.y),
                        (p_back_end.x, p_back_end.y),
                        (p_back_start.x, p_back_start.y)
                    ]
                    
                    lote = Polygon(lote_coords)
                    
                    # Verificar se o lote está dentro da quadra e atende aos critérios
                    if (lote.within(quadra) and 
                        lote.area >= area_minima and 
                        largura_real >= testada_minima):
                        self.lotes.append(lote)
    
    def alocar_areas_comuns(self):
        """
        Aloca áreas verdes e institucionais.
        Etapa 6 do algoritmo.
        """
        area_total = self.perimetro_original.area
        percentual_verde = self.parametros['percentual_area_verde'] / 100
        percentual_institucional = self.parametros['percentual_area_institucional'] / 100
        
        area_verde_necessaria = area_total * percentual_verde
        area_institucional_necessaria = area_total * percentual_institucional
        
        # Calcular área ocupada pelos lotes e ruas
        area_ocupada = sum(lote.area for lote in self.lotes)
        area_ocupada += sum(rua.area for rua in self.ruas)
        
        # Área disponível para áreas comuns
        area_disponivel = area_total - area_ocupada
        
        # Alocar áreas verdes (simplificado - usar quadras não utilizadas)
        area_verde_alocada = 0
        for quadra in self.quadras:
            if area_verde_alocada >= area_verde_necessaria:
                break
                
            # Verificar se a quadra não foi totalmente utilizada para lotes
            area_lotes_quadra = sum(lote.area for lote in self.lotes if lote.within(quadra))
            
            if area_lotes_quadra < quadra.area * 0.5:  # Se menos de 50% foi utilizada
                self.areas_verdes.append(quadra)
                area_verde_alocada += quadra.area
        
        # Alocar áreas institucionais
        area_institucional_alocada = 0
        for quadra in self.quadras:
            if area_institucional_alocada >= area_institucional_necessaria:
                break
                
            if quadra not in self.areas_verdes:
                area_lotes_quadra = sum(lote.area for lote in self.lotes if lote.within(quadra))
                
                if area_lotes_quadra < quadra.area * 0.3:  # Se menos de 30% foi utilizada
                    self.areas_institucionais.append(quadra)
                    area_institucional_alocada += quadra.area
    
    def exportar_dxf(self, arquivo_saida: str):
        """
        Exporta o resultado para arquivo DXF.
        Etapa 7 do algoritmo.
        
        Args:
            arquivo_saida: Caminho do arquivo DXF de saída
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
        Executa todo o processo de loteamento.
        
        Args:
            arquivo_entrada: Caminho do arquivo de entrada
            arquivo_saida: Caminho do arquivo DXF de saída
            
        Returns:
            Dicionário com estatísticas do resultado
        """
        try:
            # Etapa 1: Carregar perímetro
            if not self.carregar_perimetro(arquivo_entrada):
                return {'sucesso': False, 'erro': 'Erro ao carregar perímetro'}
            
            # Etapa 2: Internalizar perímetro
            self.internalizar_perimetro()
            
            # Etapa 3: Definir eixo principal
            eixo_principal = self.definir_eixo_principal()
            
            # Etapa 4: Criar malha viária
            self.criar_malha_viaria(eixo_principal)
            
            # Etapa 5: Dividir em quadras
            self.dividir_em_quadras()
            
            # Etapa 6: Subdividir quadras em lotes
            self.subdividir_quadras_em_lotes()
            
            # Etapa 7: Alocar áreas comuns
            self.alocar_areas_comuns()
            
            # Etapa 8: Exportar resultado
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

