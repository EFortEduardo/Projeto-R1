import geopandas as gpd
import shapely
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import unary_union, split, polygonize
from shapely.affinity import rotate, translate
import ezdxf
import numpy as np
import math
from typing import List, Tuple, Dict, Optional
import os

class LoteamentoProcessorAvancado:
    """
    Processador avançado de loteamento com melhorias para:
    - Geração de calçadas
    - Distribuição adequada de áreas comuns
    - Aproveitamento de áreas irregulares
    - Garantia de acesso a todos os lotes
    - Organização adequada das quadras
    """
    
    def __init__(self, parametros: Dict):
        """
        Inicializa o processador com os parâmetros fornecidos pela GUI.
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
        self.calcadas = []
        
    def _validar_e_limpar_parametros(self, parametros: Dict) -> Dict:
        """
        Valida e limpa os parâmetros, substituindo valores NaN por padrões seguros.
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
    
    def carregar_perimetro(self, arquivo_path: str) -> bool:
        """
        Carrega o perímetro do terreno a partir de arquivo DXF ou KML.
        """
        try:
            print(f"Carregando arquivo: {arquivo_path}")
            
            if not os.path.exists(arquivo_path):
                print(f"Arquivo não encontrado: {arquivo_path}")
                return False
                
            extensao = os.path.splitext(arquivo_path)[1].lower()
            
            if extensao == '.kml':
                gdf = gpd.read_file(arquivo_path)
                if len(gdf) > 0:
                    geometria = gdf.geometry.iloc[0]
                    if isinstance(geometria, MultiPolygon):
                        self.perimetro_original = max(geometria.geoms, key=lambda x: x.area)
                    elif isinstance(geometria, Polygon):
                        self.perimetro_original = geometria
                    else:
                        return False
                else:
                    return False
                    
            elif extensao == '.dxf':
                doc = ezdxf.readfile(arquivo_path)
                msp = doc.modelspace()
                
                coordenadas = []
                
                for entity in msp:
                    if entity.dxftype() == 'LWPOLYLINE' and entity.closed:
                        pontos = [(p[0], p[1]) for p in entity.get_points()]
                        coordenadas = pontos
                        break
                    elif entity.dxftype() == 'POLYLINE' and entity.is_closed:
                        pontos = [(v.dxf.location[0], v.dxf.location[1]) for v in entity.vertices]
                        coordenadas = pontos
                        break
                
                if coordenadas:
                    # Validar coordenadas para NaN
                    coordenadas_validas = []
                    for x, y in coordenadas:
                        if not (math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y)):
                            coordenadas_validas.append((x, y))
                    
                    if len(coordenadas_validas) >= 3:
                        self.perimetro_original = Polygon(coordenadas_validas)
                    else:
                        return False
                else:
                    return False
            else:
                return False
                
            # Verificar se o polígono é válido e tem área positiva
            if not self.perimetro_original.is_valid:
                self.perimetro_original = self.perimetro_original.buffer(0)
            
            if self.perimetro_original.area <= 0:
                return False
                
            print(f"Perímetro carregado. Área: {self.perimetro_original.area:.2f} m²")
            return True
            
        except Exception as e:
            print(f"Erro ao carregar perímetro: {e}")
            return False
    
    def internalizar_perimetro_com_calcadas(self):
        """
        Aplica offset negativo ao perímetro para criar vias perimetrais com calçadas.
        """
        try:
            largura_rua = self.parametros['largura_rua']
            largura_calcada = self.parametros['largura_calcada']
            
            # Calcular offset total (rua + 2 calçadas)
            offset_total = (largura_rua + 2 * largura_calcada) / 2
            
            # Criar perímetro internalizado
            self.perimetro_internalizado = self.perimetro_original.buffer(-offset_total)
            
            # Verificar se o resultado é válido
            if not self.perimetro_internalizado.is_valid or self.perimetro_internalizado.is_empty:
                # Reduzir progressivamente o offset
                for reducao in [0.8, 0.6, 0.4, 0.2]:
                    offset_reduzido = offset_total * reducao
                    self.perimetro_internalizado = self.perimetro_original.buffer(-offset_reduzido)
                    if (self.perimetro_internalizado.is_valid and 
                        not self.perimetro_internalizado.is_empty and 
                        self.perimetro_internalizado.area > 0):
                        break
                        
            # Se ainda não é válido, usar o perímetro original
            if (not self.perimetro_internalizado.is_valid or 
                self.perimetro_internalizado.is_empty or 
                self.perimetro_internalizado.area <= 0):
                self.perimetro_internalizado = self.perimetro_original.buffer(-largura_rua/2)
                
            print(f"Perímetro internalizado. Área: {self.perimetro_internalizado.area:.2f} m²")
                
        except Exception as e:
            print(f"Erro na internalização: {e}")
            self.perimetro_internalizado = self.perimetro_original
    
    def criar_sistema_viario_com_calcadas(self):
        """
        Cria um sistema viário completo com ruas e calçadas.
        """
        try:
            bounds = self.perimetro_internalizado.bounds
            min_x, min_y, max_x, max_y = bounds
            
            largura_total = max_x - min_x
            altura_total = max_y - min_y
            profundidade_max = self.parametros['profundidade_max_quadra']
            largura_rua = self.parametros['largura_rua']
            largura_calcada = self.parametros['largura_calcada']
            
            # Calcular número de linhas de forma mais inteligente
            num_linhas_verticais = max(1, int(largura_total / profundidade_max))
            num_linhas_horizontais = max(1, int(altura_total / profundidade_max))
            
            # Para terrenos pequenos, garantir pelo menos uma linha
            area_terreno = self.perimetro_internalizado.area
            if area_terreno < 5000:  # Terrenos menores que 5000 m²
                if largura_total > altura_total:
                    num_linhas_verticais = max(1, num_linhas_verticais)
                    num_linhas_horizontais = 0
                else:
                    num_linhas_horizontais = max(1, num_linhas_horizontais)
                    num_linhas_verticais = 0
            
            # Limitar número de linhas
            num_linhas_verticais = min(num_linhas_verticais, 6)
            num_linhas_horizontais = min(num_linhas_horizontais, 6)
            
            linhas_viarias = []
            
            # Criar linhas verticais
            if num_linhas_verticais > 0:
                for i in range(1, num_linhas_verticais + 1):
                    x = min_x + (i * largura_total / (num_linhas_verticais + 1))
                    linha = LineString([(x, min_y - 10), (x, max_y + 10)])
                    intersecao = linha.intersection(self.perimetro_internalizado)
                    if isinstance(intersecao, LineString) and intersecao.length > 0:
                        linhas_viarias.append(intersecao)
                    elif hasattr(intersecao, 'geoms'):
                        for geom in intersecao.geoms:
                            if isinstance(geom, LineString) and geom.length > 0:
                                linhas_viarias.append(geom)
            
            # Criar linhas horizontais
            if num_linhas_horizontais > 0:
                for i in range(1, num_linhas_horizontais + 1):
                    y = min_y + (i * altura_total / (num_linhas_horizontais + 1))
                    linha = LineString([(min_x - 10, y), (max_x + 10, y)])
                    intersecao = linha.intersection(self.perimetro_internalizado)
                    if isinstance(intersecao, LineString) and intersecao.length > 0:
                        linhas_viarias.append(intersecao)
                    elif hasattr(intersecao, 'geoms'):
                        for geom in intersecao.geoms:
                            if isinstance(geom, LineString) and geom.length > 0:
                                linhas_viarias.append(geom)
            
            # Se não conseguiu criar linhas, criar pelo menos uma linha central
            if not linhas_viarias:
                if largura_total > altura_total:
                    # Linha vertical central
                    x_centro = min_x + largura_total / 2
                    linha_central = LineString([(x_centro, min_y), (x_centro, max_y)])
                else:
                    # Linha horizontal central
                    y_centro = min_y + altura_total / 2
                    linha_central = LineString([(min_x, y_centro), (max_x, y_centro)])
                
                intersecao_central = linha_central.intersection(self.perimetro_internalizado)
                if isinstance(intersecao_central, LineString) and intersecao_central.length > 0:
                    linhas_viarias.append(intersecao_central)
            
            self.malha_viaria = linhas_viarias
            
            # Criar ruas (leito carroçável) e calçadas
            if self.malha_viaria:
                linhas_unidas = unary_union(self.malha_viaria)
                
                # Criar ruas
                ruas_buffer = linhas_unidas.buffer(largura_rua / 2)
                if isinstance(ruas_buffer, Polygon):
                    self.ruas = [ruas_buffer]
                elif hasattr(ruas_buffer, 'geoms'):
                    self.ruas = [geom for geom in ruas_buffer.geoms if isinstance(geom, Polygon)]
                else:
                    self.ruas = []
                
                # Criar calçadas
                calcadas_buffer = linhas_unidas.buffer((largura_rua + 2 * largura_calcada) / 2)
                if self.ruas:
                    ruas_unidas = unary_union(self.ruas)
                    area_calcadas = calcadas_buffer.difference(ruas_unidas)
                    
                    if isinstance(area_calcadas, Polygon):
                        self.calcadas = [area_calcadas]
                    elif hasattr(area_calcadas, 'geoms'):
                        self.calcadas = [geom for geom in area_calcadas.geoms if isinstance(geom, Polygon)]
                    else:
                        self.calcadas = []
                else:
                    self.calcadas = []
            else:
                self.ruas = []
                self.calcadas = []
                
            print(f"Sistema viário criado: {len(self.ruas)} ruas, {len(self.calcadas)} calçadas")
                
        except Exception as e:
            print(f"Erro na criação do sistema viário: {e}")
            self.malha_viaria = []
            self.ruas = []
            self.calcadas = []
    
    def dividir_em_quadras_inteligente(self):
        """
        Divide o terreno em quadras de forma inteligente, considerando a forma irregular.
        """
        try:
            if not self.malha_viaria:
                self.quadras = [self.perimetro_internalizado]
                return
            
            largura_rua = self.parametros['largura_rua']
            largura_calcada = self.parametros['largura_calcada']
            buffer_total = (largura_rua + 2 * largura_calcada) / 2
            
            linhas_unidas = unary_union(self.malha_viaria)
            sistema_viario_total = linhas_unidas.buffer(buffer_total)
            
            # Subtrair o sistema viário do perímetro internalizado
            area_quadras = self.perimetro_internalizado.difference(sistema_viario_total)
            
            if isinstance(area_quadras, MultiPolygon):
                quadras_candidatas = list(area_quadras.geoms)
            elif isinstance(area_quadras, Polygon) and not area_quadras.is_empty:
                quadras_candidatas = [area_quadras]
            else:
                quadras_candidatas = [self.perimetro_internalizado]
            
            # Filtrar quadras muito pequenas
            area_minima_quadra = self.parametros['area_minima_lote'] * 3  # Pelo menos 3 lotes por quadra
            self.quadras = [q for q in quadras_candidatas if q.area >= area_minima_quadra and q.is_valid]
            
            if not self.quadras:
                self.quadras = [self.perimetro_internalizado]
                
            print(f"Quadras criadas: {len(self.quadras)}")
            for i, quadra in enumerate(self.quadras):
                print(f"  Quadra {i+1}: {quadra.area:.2f} m²")
                
        except Exception as e:
            print(f"Erro na divisão em quadras: {e}")
            self.quadras = [self.perimetro_internalizado]
    
    def subdividir_quadras_com_acesso_garantido(self):
        """
        Subdivide quadras em lotes garantindo que todos tenham acesso à rua.
        Inclui criação de lotes irregulares para melhor aproveitamento.
        """
        try:
            area_minima = self.parametros['area_minima_lote']
            testada_minima = self.parametros['testada_minima_lote']
            largura_padrao = self.parametros['largura_padrao_lote']
            profundidade_padrao = self.parametros['profundidade_padrao_lote']
            
            self.lotes = []
            
            for i, quadra in enumerate(self.quadras):
                print(f"Processando quadra {i+1}: área = {quadra.area:.2f} m²")
                
                if quadra.area < area_minima * 1.5:
                    # Quadra muito pequena, usar como lote único se tiver acesso
                    if self._quadra_tem_acesso_rua(quadra):
                        self.lotes.append(quadra)
                        print(f"  Quadra {i+1} convertida em lote único")
                    continue
                
                # Estratégia 1: Lotes regulares ao longo das bordas com rua
                lotes_regulares = self._criar_lotes_regulares_com_acesso(quadra, area_minima, testada_minima, largura_padrao, profundidade_padrao)
                
                # Estratégia 2: Lotes irregulares nas áreas restantes
                area_restante = self._calcular_area_restante_apos_lotes_regulares(quadra, lotes_regulares)
                lotes_irregulares = self._criar_lotes_irregulares(area_restante, area_minima, testada_minima)
                
                # Combinar lotes regulares e irregulares
                lotes_quadra = lotes_regulares + lotes_irregulares
                
                self.lotes.extend(lotes_quadra)
                print(f"  Lotes criados na quadra {i+1}: {len(lotes_regulares)} regulares + {len(lotes_irregulares)} irregulares = {len(lotes_quadra)} total")
                
            print(f"Total de lotes criados: {len(self.lotes)}")
                
        except Exception as e:
            print(f"Erro na subdivisão de quadras: {e}")
    
    def _quadra_tem_acesso_rua(self, quadra: Polygon) -> bool:
        """
        Verifica se a quadra tem acesso direto à rua.
        """
        try:
            for rua in self.ruas:
                if quadra.distance(rua) < 2.0:  # Tolerância de 2 metros
                    return True
            return False
        except:
            return False
    
    def _criar_lotes_regulares_com_acesso(self, quadra: Polygon, area_minima: float, 
                                        testada_minima: float, largura_padrao: float, 
                                        profundidade_padrao: float) -> List[Polygon]:
        """
        Cria lotes regulares ao longo das bordas que têm acesso à rua.
        """
        lotes = []
        
        try:
            # Encontrar bordas com acesso à rua
            bordas_com_rua = self._encontrar_bordas_com_rua(quadra)
            
            if not bordas_com_rua:
                return lotes
            
            for borda in bordas_com_rua:
                lotes_borda = self._criar_lotes_ao_longo_da_borda(quadra, borda, area_minima, testada_minima, largura_padrao, profundidade_padrao)
                lotes.extend(lotes_borda)
                
        except Exception as e:
            print(f"Erro ao criar lotes regulares: {e}")
            
        return lotes
    
    def _criar_lotes_ao_longo_da_borda(self, quadra: Polygon, borda: LineString, 
                                     area_minima: float, testada_minima: float, 
                                     largura_padrao: float, profundidade_padrao: float) -> List[Polygon]:
        """
        Cria lotes ao longo de uma borda específica.
        """
        lotes = []
        
        try:
            comprimento_borda = borda.length
            
            # Calcular número de lotes
            num_lotes = max(1, int(comprimento_borda / largura_padrao))
            largura_lote = comprimento_borda / num_lotes
            
            # Ajustar se a largura for menor que o mínimo
            if largura_lote < testada_minima:
                num_lotes = max(1, int(comprimento_borda / testada_minima))
                largura_lote = comprimento_borda / num_lotes
            
            # Criar lotes
            for j in range(num_lotes):
                lote = self._criar_lote_retangular_adaptativo(quadra, borda, j, num_lotes, largura_lote, profundidade_padrao, area_minima)
                if lote and lote.area >= area_minima:
                    lotes.append(lote)
                    
        except Exception as e:
            print(f"Erro ao criar lotes ao longo da borda: {e}")
            
        return lotes
    
    def _criar_lote_retangular_adaptativo(self, quadra: Polygon, borda: LineString, 
                                        indice: int, total_lotes: int, largura_lote: float, 
                                        profundidade: float, area_minima: float) -> Optional[Polygon]:
        """
        Cria um lote retangular que se adapta à forma da quadra.
        """
        try:
            # Calcular posição ao longo da borda
            inicio = indice / total_lotes
            fim = (indice + 1) / total_lotes
            
            ponto_inicio = borda.interpolate(inicio, normalized=True)
            ponto_fim = borda.interpolate(fim, normalized=True)
            
            # Calcular vetor da borda
            dx = ponto_fim.x - ponto_inicio.x
            dy = ponto_fim.y - ponto_inicio.y
            
            # Vetor perpendicular (para dentro da quadra)
            perp_x = -dy
            perp_y = dx
            
            # Normalizar
            comprimento = math.sqrt(perp_x**2 + perp_y**2)
            if comprimento > 0:
                perp_x /= comprimento
                perp_y /= comprimento
            
            # Tentar diferentes profundidades para se adaptar à quadra
            for prof_tentativa in [profundidade, profundidade * 0.8, profundidade * 0.6, profundidade * 1.2]:
                # Criar retângulo
                p1 = (ponto_inicio.x, ponto_inicio.y)
                p2 = (ponto_fim.x, ponto_fim.y)
                p3 = (ponto_fim.x + perp_x * prof_tentativa, ponto_fim.y + perp_y * prof_tentativa)
                p4 = (ponto_inicio.x + perp_x * prof_tentativa, ponto_inicio.y + perp_y * prof_tentativa)
                
                lote_tentativa = Polygon([p1, p2, p3, p4])
                
                # Intersectar com a quadra
                lote_final = lote_tentativa.intersection(quadra)
                
                if isinstance(lote_final, Polygon) and lote_final.area >= area_minima:
                    return lote_final
            
            return None
                
        except Exception as e:
            print(f"Erro ao criar lote retangular adaptativo: {e}")
            return None
    
    def _calcular_area_restante_apos_lotes_regulares(self, quadra: Polygon, lotes_regulares: List[Polygon]) -> Polygon:
        """
        Calcula a área restante da quadra após a criação dos lotes regulares.
        """
        try:
            if not lotes_regulares:
                return quadra
            
            area_lotes = unary_union(lotes_regulares)
            area_restante = quadra.difference(area_lotes)
            
            if isinstance(area_restante, Polygon) and not area_restante.is_empty:
                return area_restante
            elif isinstance(area_restante, MultiPolygon):
                # Retornar a maior área
                return max(area_restante.geoms, key=lambda x: x.area)
            else:
                return Polygon()  # Área vazia
                
        except Exception as e:
            print(f"Erro ao calcular área restante: {e}")
            return Polygon()
    
    def _criar_lotes_irregulares(self, area_restante: Polygon, area_minima: float, testada_minima: float) -> List[Polygon]:
        """
        Cria lotes irregulares na área restante, adaptando-se à forma disponível.
        """
        lotes_irregulares = []
        
        try:
            if area_restante.is_empty or area_restante.area < area_minima:
                return lotes_irregulares
            
            # Estratégia 1: Dividir por triangulação adaptativa
            lotes_triangulacao = self._dividir_por_triangulacao_adaptativa(area_restante, area_minima)
            
            # Estratégia 2: Dividir por linhas de corte inteligentes
            if not lotes_triangulacao:
                lotes_corte = self._dividir_por_cortes_inteligentes(area_restante, area_minima, testada_minima)
                lotes_irregulares.extend(lotes_corte)
            else:
                lotes_irregulares.extend(lotes_triangulacao)
            
            # Filtrar lotes muito pequenos
            lotes_irregulares = [lote for lote in lotes_irregulares if lote.area >= area_minima]
            
        except Exception as e:
            print(f"Erro ao criar lotes irregulares: {e}")
            
        return lotes_irregulares
    
    def _dividir_por_triangulacao_adaptativa(self, area: Polygon, area_minima: float) -> List[Polygon]:
        """
        Divide a área usando triangulação adaptativa.
        """
        lotes = []
        
        try:
            # Obter vértices do polígono
            coords = list(area.exterior.coords)[:-1]  # Remover último ponto duplicado
            
            if len(coords) < 3:
                return lotes
            
            # Para polígonos simples, tentar divisão por diagonais
            if len(coords) <= 6:  # Hexágono ou menos
                # Dividir em triângulos e depois agrupar
                triangulos = self._triangular_poligono(coords)
                lotes_agrupados = self._agrupar_triangulos(triangulos, area_minima)
                lotes.extend(lotes_agrupados)
            else:
                # Para polígonos complexos, usar estratégia de corte
                lotes_corte = self._dividir_por_cortes_inteligentes(area, area_minima, 8.0)
                lotes.extend(lotes_corte)
                
        except Exception as e:
            print(f"Erro na triangulação adaptativa: {e}")
            
        return lotes
    
    def _triangular_poligono(self, coords: List[Tuple[float, float]]) -> List[Polygon]:
        """
        Triangula um polígono simples.
        """
        triangulos = []
        
        try:
            if len(coords) < 3:
                return triangulos
            
            # Triangulação simples por "ear clipping" básico
            vertices = coords.copy()
            
            while len(vertices) > 3:
                # Encontrar uma "orelha" (vértice convexo)
                for i in range(len(vertices)):
                    v1 = vertices[i]
                    v2 = vertices[(i + 1) % len(vertices)]
                    v3 = vertices[(i + 2) % len(vertices)]
                    
                    # Criar triângulo
                    triangulo = Polygon([v1, v2, v3])
                    
                    if triangulo.area > 0:  # Triângulo válido
                        triangulos.append(triangulo)
                        # Remover vértice do meio
                        vertices.pop((i + 1) % len(vertices))
                        break
                else:
                    # Se não encontrou orelha, parar
                    break
            
            # Adicionar último triângulo
            if len(vertices) == 3:
                triangulo_final = Polygon(vertices)
                if triangulo_final.area > 0:
                    triangulos.append(triangulo_final)
                    
        except Exception as e:
            print(f"Erro na triangulação: {e}")
            
        return triangulos
    
    def _agrupar_triangulos(self, triangulos: List[Polygon], area_minima: float) -> List[Polygon]:
        """
        Agrupa triângulos pequenos para formar lotes maiores.
        """
        lotes = []
        
        try:
            triangulos_restantes = triangulos.copy()
            
            while triangulos_restantes:
                triangulo_atual = triangulos_restantes.pop(0)
                
                if triangulo_atual.area >= area_minima:
                    lotes.append(triangulo_atual)
                else:
                    # Tentar agrupar com triângulos adjacentes
                    agrupado = triangulo_atual
                    
                    for i, outro_triangulo in enumerate(triangulos_restantes):
                        if agrupado.touches(outro_triangulo):
                            agrupado = agrupado.union(outro_triangulo)
                            triangulos_restantes.pop(i)
                            
                            if agrupado.area >= area_minima:
                                break
                    
                    if agrupado.area >= area_minima * 0.8:  # Tolerância de 80%
                        lotes.append(agrupado)
                        
        except Exception as e:
            print(f"Erro ao agrupar triângulos: {e}")
            
        return lotes
    
    def _dividir_por_cortes_inteligentes(self, area: Polygon, area_minima: float, testada_minima: float) -> List[Polygon]:
        """
        Divide a área usando cortes inteligentes baseados na geometria.
        """
        lotes = []
        
        try:
            if area.area < area_minima * 2:
                # Área muito pequena para dividir
                if area.area >= area_minima:
                    lotes.append(area)
                return lotes
            
            # Obter bounding box
            bounds = area.bounds
            min_x, min_y, max_x, max_y = bounds
            
            largura = max_x - min_x
            altura = max_y - min_y
            
            # Decidir direção do corte baseado na proporção
            if largura > altura * 1.5:
                # Corte vertical
                linha_corte = LineString([(min_x + largura/2, min_y - 10), (min_x + largura/2, max_y + 10)])
            else:
                # Corte horizontal
                linha_corte = LineString([(min_x - 10, min_y + altura/2), (max_x + 10, min_y + altura/2)])
            
            # Aplicar corte
            try:
                partes = split(area, linha_corte)
                if hasattr(partes, 'geoms'):
                    partes_lista = list(partes.geoms)
                else:
                    partes_lista = [partes]
                
                # Processar cada parte recursivamente
                for parte in partes_lista:
                    if isinstance(parte, Polygon) and parte.area >= area_minima:
                        if parte.area < area_minima * 3:
                            # Parte pequena o suficiente, usar como lote
                            lotes.append(parte)
                        else:
                            # Parte ainda grande, dividir recursivamente
                            sublotes = self._dividir_por_cortes_inteligentes(parte, area_minima, testada_minima)
                            lotes.extend(sublotes)
                            
            except:
                # Se o corte falhar, usar a área original
                if area.area >= area_minima:
                    lotes.append(area)
                    
        except Exception as e:
            print(f"Erro nos cortes inteligentes: {e}")
            
        return lotes
    
    def _encontrar_bordas_com_rua(self, quadra: Polygon) -> List[LineString]:
        """
        Encontra as bordas da quadra que fazem interface com ruas.
        """
        bordas_com_rua = []
        
        try:
            # Obter o contorno da quadra
            contorno = quadra.exterior
            
            # Dividir o contorno em segmentos
            coords = list(contorno.coords)
            
            for i in range(len(coords) - 1):
                segmento = LineString([coords[i], coords[i + 1]])
                
                # Verificar se este segmento está próximo de uma rua
                for rua in self.ruas:
                    if segmento.distance(rua) < 1.0:  # Tolerância de 1 metro
                        bordas_com_rua.append(segmento)
                        break
                        
        except Exception as e:
            print(f"Erro ao encontrar bordas com rua: {e}")
            
        return bordas_com_rua
    
    def _criar_lotes_com_testada(self, quadra: Polygon, bordas_com_rua: List[LineString], 
                                area_minima: float, testada_minima: float, 
                                largura_padrao: float, profundidade_padrao: float) -> List[Polygon]:
        """
        Cria lotes ao longo das bordas que têm acesso à rua.
        """
        lotes = []
        
        try:
            for borda in bordas_com_rua:
                # Calcular quantos lotes cabem ao longo desta borda
                comprimento_borda = borda.length
                num_lotes = max(1, int(comprimento_borda / largura_padrao))
                
                if num_lotes == 0:
                    continue
                
                largura_lote = comprimento_borda / num_lotes
                
                # Verificar se a largura atende ao mínimo
                if largura_lote < testada_minima:
                    num_lotes = max(1, int(comprimento_borda / testada_minima))
                    largura_lote = comprimento_borda / num_lotes
                
                # Criar lotes ao longo desta borda
                for j in range(num_lotes):
                    try:
                        lote = self._criar_lote_individual(quadra, borda, j, num_lotes, 
                                                         largura_lote, profundidade_padrao, area_minima)
                        if lote and lote.area >= area_minima:
                            lotes.append(lote)
                    except Exception as e:
                        print(f"Erro ao criar lote individual: {e}")
                        continue
                        
        except Exception as e:
            print(f"Erro ao criar lotes com testada: {e}")
            
        return lotes
    
    def _criar_lote_individual(self, quadra: Polygon, borda: LineString, indice: int, 
                             total_lotes: int, largura_lote: float, profundidade: float, 
                             area_minima: float) -> Optional[Polygon]:
        """
        Cria um lote individual ao longo de uma borda.
        """
        try:
            # Obter pontos da borda
            coords_borda = list(borda.coords)
            
            # Calcular posição do lote ao longo da borda
            inicio = indice / total_lotes
            fim = (indice + 1) / total_lotes
            
            # Interpolar pontos ao longo da borda
            ponto_inicio = borda.interpolate(inicio, normalized=True)
            ponto_fim = borda.interpolate(fim, normalized=True)
            
            # Calcular vetor perpendicular à borda (para dentro da quadra)
            dx = ponto_fim.x - ponto_inicio.x
            dy = ponto_fim.y - ponto_inicio.y
            
            # Vetor perpendicular (rotação de 90 graus)
            perp_x = -dy
            perp_y = dx
            
            # Normalizar o vetor perpendicular
            comprimento = math.sqrt(perp_x**2 + perp_y**2)
            if comprimento > 0:
                perp_x /= comprimento
                perp_y /= comprimento
            
            # Criar retângulo do lote
            p1 = (ponto_inicio.x, ponto_inicio.y)
            p2 = (ponto_fim.x, ponto_fim.y)
            p3 = (ponto_fim.x + perp_x * profundidade, ponto_fim.y + perp_y * profundidade)
            p4 = (ponto_inicio.x + perp_x * profundidade, ponto_inicio.y + perp_y * profundidade)
            
            lote_retangular = Polygon([p1, p2, p3, p4])
            
            # Intersectar com a quadra para obter a forma final
            lote_final = lote_retangular.intersection(quadra)
            
            if isinstance(lote_final, Polygon) and lote_final.area >= area_minima:
                return lote_final
            else:
                return None
                
        except Exception as e:
            print(f"Erro ao criar lote individual: {e}")
            return None
    
    def alocar_areas_comuns_estrategicamente(self):
        """
        Aloca áreas verdes e institucionais de forma estratégica e inteligente.
        """
        try:
            area_total = self.perimetro_original.area
            percentual_verde = self.parametros['percentual_area_verde'] / 100
            percentual_institucional = self.parametros['percentual_area_institucional'] / 100
            
            area_verde_necessaria = area_total * percentual_verde
            area_institucional_necessaria = area_total * percentual_institucional
            
            print(f"Área verde necessária: {area_verde_necessaria:.2f} m² ({percentual_verde*100:.1f}%)")
            print(f"Área institucional necessária: {area_institucional_necessaria:.2f} m² ({percentual_institucional*100:.1f}%)")
            
            # Estratégia 1: Usar áreas não utilizadas (sobras das quadras)
            self._alocar_areas_sobras()
            
            # Estratégia 2: Converter quadras pequenas em áreas comuns
            self._converter_quadras_pequenas_em_areas_comuns(area_verde_necessaria, area_institucional_necessaria)
            
            # Estratégia 3: Criar áreas comuns em cantos e irregularidades
            self._criar_areas_em_irregularidades(area_verde_necessaria, area_institucional_necessaria)
            
            # Calcular áreas alocadas
            area_verde_alocada = sum(area.area for area in self.areas_verdes)
            area_institucional_alocada = sum(area.area for area in self.areas_institucionais)
            
            print(f"Áreas verdes alocadas: {len(self.areas_verdes)} ({area_verde_alocada:.2f} m²)")
            print(f"Áreas institucionais alocadas: {len(self.areas_institucionais)} ({area_institucional_alocada:.2f} m²)")
                
        except Exception as e:
            print(f"Erro na alocação de áreas comuns: {e}")
    
    def _alocar_areas_sobras(self):
        """
        Aloca áreas que sobraram após a criação de lotes.
        """
        try:
            # Calcular área utilizada
            geometrias_utilizadas = []
            geometrias_utilizadas.extend(self.lotes)
            geometrias_utilizadas.extend(self.ruas)
            geometrias_utilizadas.extend(self.calcadas)
            
            if geometrias_utilizadas:
                area_utilizada = unary_union(geometrias_utilizadas)
                area_disponivel = self.perimetro_internalizado.difference(area_utilizada)
                
                if isinstance(area_disponivel, MultiPolygon):
                    areas_disponiveis = list(area_disponivel.geoms)
                elif isinstance(area_disponivel, Polygon) and not area_disponivel.is_empty:
                    areas_disponiveis = [area_disponivel]
                else:
                    areas_disponiveis = []
                
                # Filtrar áreas muito pequenas (menos de 50 m²)
                areas_disponiveis = [area for area in areas_disponiveis if area.area >= 50.0]
                
                # Ordenar por tamanho (maiores primeiro)
                areas_disponiveis.sort(key=lambda x: x.area, reverse=True)
                
                # Alocar como áreas verdes (parques/praças são prioritários)
                for area in areas_disponiveis:
                    self.areas_verdes.append(area)
                    
        except Exception as e:
            print(f"Erro ao alocar áreas sobras: {e}")
    
    def _converter_quadras_pequenas_em_areas_comuns(self, area_verde_necessaria: float, area_institucional_necessaria: float):
        """
        Converte quadras muito pequenas para loteamento em áreas comuns.
        """
        try:
            area_minima_quadra = self.parametros['area_minima_lote'] * 4  # Pelo menos 4 lotes
            
            quadras_pequenas = []
            quadras_mantidas = []
            
            for quadra in self.quadras:
                if quadra.area < area_minima_quadra:
                    quadras_pequenas.append(quadra)
                else:
                    quadras_mantidas.append(quadra)
            
            # Atualizar lista de quadras
            self.quadras = quadras_mantidas
            
            # Alocar quadras pequenas como áreas comuns
            area_verde_atual = sum(area.area for area in self.areas_verdes)
            area_institucional_atual = sum(area.area for area in self.areas_institucionais)
            
            for quadra in quadras_pequenas:
                if area_verde_atual < area_verde_necessaria:
                    self.areas_verdes.append(quadra)
                    area_verde_atual += quadra.area
                elif area_institucional_atual < area_institucional_necessaria:
                    self.areas_institucionais.append(quadra)
                    area_institucional_atual += quadra.area
                else:
                    # Se já atingiu os percentuais, adicionar como área verde
                    self.areas_verdes.append(quadra)
                    
        except Exception as e:
            print(f"Erro ao converter quadras pequenas: {e}")
    
    def _criar_areas_em_irregularidades(self, area_verde_necessaria: float, area_institucional_necessaria: float):
        """
        Cria áreas comuns em cantos e irregularidades do terreno.
        """
        try:
            # Identificar cantos e irregularidades do perímetro original
            # que não foram bem aproveitados
            
            # Calcular diferença entre perímetro original e internalizado
            area_perimetral = self.perimetro_original.difference(self.perimetro_internalizado)
            
            if isinstance(area_perimetral, MultiPolygon):
                areas_perimetrais = list(area_perimetral.geoms)
            elif isinstance(area_perimetral, Polygon) and not area_perimetral.is_empty:
                areas_perimetrais = [area_perimetral]
            else:
                areas_perimetrais = []
            
            # Filtrar áreas perimetrais significativas (maiores que 100 m²)
            areas_significativas = [area for area in areas_perimetrais if area.area >= 100.0]
            
            area_verde_atual = sum(area.area for area in self.areas_verdes)
            area_institucional_atual = sum(area.area for area in self.areas_institucionais)
            
            for area in areas_significativas:
                if area_verde_atual < area_verde_necessaria:
                    self.areas_verdes.append(area)
                    area_verde_atual += area.area
                elif area_institucional_atual < area_institucional_necessaria:
                    self.areas_institucionais.append(area)
                    area_institucional_atual += area.area
                    
        except Exception as e:
            print(f"Erro ao criar áreas em irregularidades: {e}")
    
    def exportar_dxf_completo(self, arquivo_saida: str):
        """
        Exporta o resultado completo para DXF com todas as camadas.
        """
        try:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            # Criar layers com cores específicas
            doc.layers.new('PERIMETRO', dxfattribs={'color': 1})      # Vermelho
            doc.layers.new('RUAS', dxfattribs={'color': 2})           # Amarelo
            doc.layers.new('CALCADAS', dxfattribs={'color': 8})       # Cinza
            doc.layers.new('QUADRAS', dxfattribs={'color': 3})        # Verde
            doc.layers.new('LOTES', dxfattribs={'color': 4})          # Ciano
            doc.layers.new('AREA_VERDE', dxfattribs={'color': 5})     # Azul
            doc.layers.new('AREA_INST', dxfattribs={'color': 6})      # Magenta
            
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
            
            # Adicionar calçadas
            for calcada in self.calcadas:
                if isinstance(calcada, Polygon):
                    coords = coords_validas(calcada.exterior.coords)
                    if len(coords) >= 3:
                        msp.add_lwpolyline(coords, close=True, dxfattribs={'layer': 'CALCADAS'})
            
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
            print(f"Arquivo DXF salvo: {arquivo_saida}")
            
        except Exception as e:
            print(f"Erro na exportação DXF: {e}")
            raise
    
    def processar_loteamento_avancado(self, arquivo_entrada: str, arquivo_saida: str) -> Dict:
        """
        Executa todo o processo de loteamento avançado.
        """
        try:
            print("=== PROCESSAMENTO AVANÇADO DE LOTEAMENTO ===")
            
            # Etapa 1: Carregar perímetro
            print("1. Carregando perímetro...")
            if not self.carregar_perimetro(arquivo_entrada):
                return {'sucesso': False, 'erro': 'Erro ao carregar perímetro'}
            
            # Etapa 2: Internalizar perímetro com calçadas
            print("2. Internalizando perímetro com calçadas...")
            self.internalizar_perimetro_com_calcadas()
            
            # Etapa 3: Criar sistema viário com calçadas
            print("3. Criando sistema viário com calçadas...")
            self.criar_sistema_viario_com_calcadas()
            
            # Etapa 4: Dividir em quadras inteligente
            print("4. Dividindo em quadras de forma inteligente...")
            self.dividir_em_quadras_inteligente()
            
            # Etapa 5: Subdividir quadras com acesso garantido
            print("5. Subdividindo quadras com acesso garantido...")
            self.subdividir_quadras_com_acesso_garantido()
            
            # Etapa 6: Alocar áreas comuns estrategicamente
            print("6. Alocando áreas comuns estrategicamente...")
            self.alocar_areas_comuns_estrategicamente()
            
            # Etapa 7: Exportar resultado
            print("7. Exportando resultado...")
            self.exportar_dxf_completo(arquivo_saida)
            
            # Calcular estatísticas
            area_total = self.perimetro_original.area
            num_lotes = len(self.lotes)
            area_lotes = sum(lote.area for lote in self.lotes if lote.area > 0)
            area_ruas = sum(rua.area for rua in self.ruas if rua.area > 0)
            area_calcadas = sum(calcada.area for calcada in self.calcadas if calcada.area > 0)
            area_verde = sum(area.area for area in self.areas_verdes if area.area > 0)
            area_institucional = sum(area.area for area in self.areas_institucionais if area.area > 0)
            
            estatisticas = {
                'sucesso': True,
                'area_total': area_total,
                'num_lotes': num_lotes,
                'area_lotes': area_lotes,
                'area_ruas': area_ruas,
                'area_calcadas': area_calcadas,
                'area_verde': area_verde,
                'area_institucional': area_institucional,
                'percentual_lotes': (area_lotes / area_total) * 100 if area_total > 0 else 0,
                'percentual_ruas': (area_ruas / area_total) * 100 if area_total > 0 else 0,
                'percentual_calcadas': (area_calcadas / area_total) * 100 if area_total > 0 else 0,
                'percentual_verde': (area_verde / area_total) * 100 if area_total > 0 else 0,
                'percentual_institucional': (area_institucional / area_total) * 100 if area_total > 0 else 0
            }
            
            print("=== PROCESSAMENTO CONCLUÍDO ===")
            return estatisticas
            
        except Exception as e:
            return {'sucesso': False, 'erro': f'Erro no processamento: {str(e)}'}

