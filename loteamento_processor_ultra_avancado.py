import geopandas as gpd
import numpy as np
import math
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import unary_union, split
from shapely.affinity import rotate, translate, scale
import ezdxf
from typing import List, Tuple, Optional, Dict, Any
import random

class LoteamentoProcessorUltraAvancado:
    """
    Processador ultra-avançado de loteamento urbano com:
    - Subdivisão otimizada de lotes irregulares
    - Distribuição inteligente dentro das quadras
    - Liberdade criativa total na formação de quadras
    - Otimização de lotes de esquina
    """
    
    def __init__(self, parametros: dict):
        self.parametros = parametros
        self.perimetro_original = None
        self.perimetro_internalizado = None
        self.malha_viaria = []
        self.ruas = []
        self.calcadas = []
        self.quadras = []
        self.lotes = []
        self.areas_verdes = []
        self.areas_institucionais = []
        
        # Configurações avançadas baseadas nos parâmetros
        self.configurar_estrategias_avancadas()
    
    def configurar_estrategias_avancadas(self):
        """
        Configura estratégias avançadas baseadas nos parâmetros do usuário.
        """
        # Configurar tolerância de forma
        tolerancia = self.parametros.get('tolerancia_forma', 'Alta (Mais Irregular)')
        if 'Baixa' in tolerancia:
            self.fator_irregularidade = 0.2
        elif 'Média' in tolerancia:
            self.fator_irregularidade = 0.5
        else:  # Alta
            self.fator_irregularidade = 0.8
        
        # Configurar liberdade criativa
        liberdade = self.parametros.get('liberdade_criativa', 'Máxima')
        if liberdade == 'Conservadora':
            self.fator_criatividade = 0.2
        elif liberdade == 'Moderada':
            self.fator_criatividade = 0.4
        elif liberdade == 'Criativa':
            self.fator_criatividade = 0.7
        else:  # Máxima
            self.fator_criatividade = 1.0
        
        # Configurar densidade
        densidade = self.parametros.get('densidade_lotes', 'Alta')
        if densidade == 'Baixa':
            self.fator_densidade = 0.6
        elif densidade == 'Média':
            self.fator_densidade = 0.8
        elif densidade == 'Alta':
            self.fator_densidade = 1.0
        else:  # Máxima
            self.fator_densidade = 1.3
    
    def carregar_perimetro(self, arquivo_path: str) -> bool:
        """
        Carrega o perímetro do arquivo DXF ou KML.
        """
        try:
            print(f"Carregando arquivo: {arquivo_path}")
            
            if arquivo_path.lower().endswith('.dxf'):
                return self._carregar_dxf(arquivo_path)
            elif arquivo_path.lower().endswith('.kml'):
                return self._carregar_kml(arquivo_path)
            else:
                print("Formato de arquivo não suportado")
                return False
                
        except Exception as e:
            print(f"Erro ao carregar perímetro: {e}")
            return False
    
    def _carregar_dxf(self, arquivo_path: str) -> bool:
        """Carrega perímetro de arquivo DXF"""
        try:
            doc = ezdxf.readfile(arquivo_path)
            msp = doc.modelspace()
            
            pontos = []
            for entity in msp:
                if entity.dxftype() == 'LWPOLYLINE':
                    pontos = [(p[0], p[1]) for p in entity.get_points()]
                    break
                elif entity.dxftype() == 'POLYLINE':
                    pontos = [(v.dxf.location[0], v.dxf.location[1]) for v in entity.vertices]
                    break
            
            if len(pontos) >= 3:
                if pontos[0] != pontos[-1]:
                    pontos.append(pontos[0])
                
                self.perimetro_original = Polygon(pontos)
                print(f"Perímetro carregado. Área: {self.perimetro_original.area:.2f} m²")
                return True
            
            return False
            
        except Exception as e:
            print(f"Erro ao carregar DXF: {e}")
            return False
    
    def _carregar_kml(self, arquivo_path: str) -> bool:
        """Carrega perímetro de arquivo KML"""
        try:
            gdf = gpd.read_file(arquivo_path)
            if not gdf.empty:
                geometry = gdf.geometry.iloc[0]
                if isinstance(geometry, Polygon):
                    self.perimetro_original = geometry
                    print(f"Perímetro carregado. Área: {self.perimetro_original.area:.2f} m²")
                    return True
            return False
        except Exception as e:
            print(f"Erro ao carregar KML: {e}")
            return False
    
    def processar_loteamento_ultra_avancado(self, arquivo_entrada: str, arquivo_saida: str) -> Dict[str, Any]:
        """
        Executa o processamento ultra-avançado completo.
        """
        try:
            print("=== PROCESSAMENTO ULTRA-AVANÇADO DE LOTEAMENTO ===")
            
            # 1. Carregar perímetro
            print("1. Carregando perímetro...")
            if not self.carregar_perimetro(arquivo_entrada):
                return {'sucesso': False, 'erro': 'Erro ao carregar perímetro'}
            
            # 2. Internalizar com calçadas
            print("2. Internalizando perímetro com calçadas...")
            self.internalizar_perimetro_com_calcadas()
            
            # 3. Criar sistema viário criativo
            print("3. Criando sistema viário criativo...")
            self.criar_sistema_viario_criativo()
            
            # 4. Formar quadras com liberdade criativa
            print("4. Formando quadras com liberdade criativa...")
            self.formar_quadras_criativas()
            
            # 5. Subdividir com otimização avançada
            print("5. Subdividindo com otimização avançada...")
            self.subdividir_quadras_ultra_otimizado()
            
            # 6. Alocar áreas comuns estrategicamente
            print("6. Alocando áreas comuns estrategicamente...")
            self.alocar_areas_comuns_estrategicamente()
            
            # 7. Exportar resultado
            print("7. Exportando resultado...")
            self.exportar_dxf_ultra_avancado(arquivo_saida)
            
            # Calcular estatísticas
            estatisticas = self.calcular_estatisticas_detalhadas()
            
            print("=== PROCESSAMENTO CONCLUÍDO ===")
            
            return {
                'sucesso': True,
                **estatisticas
            }
            
        except Exception as e:
            print(f"Erro no processamento: {e}")
            return {'sucesso': False, 'erro': str(e)}
    
    def internalizar_perimetro_com_calcadas(self):
        """
        Internaliza o perímetro considerando calçadas.
        """
        try:
            largura_calcada = self.parametros['largura_calcada']
            offset_distance = largura_calcada + 1.0  # Margem adicional
            
            perimetro_internalizado = self.perimetro_original.buffer(-offset_distance)
            
            if isinstance(perimetro_internalizado, Polygon) and not perimetro_internalizado.is_empty:
                self.perimetro_internalizado = perimetro_internalizado
            else:
                # Se o buffer negativo falhar, usar 80% do perímetro original
                centroid = self.perimetro_original.centroid
                self.perimetro_internalizado = scale(self.perimetro_original, xfact=0.8, yfact=0.8, origin=centroid)
            
            print(f"Perímetro internalizado. Área: {self.perimetro_internalizado.area:.2f} m²")
            
        except Exception as e:
            print(f"Erro na internalização: {e}")
            self.perimetro_internalizado = self.perimetro_original
    
    def criar_sistema_viario_criativo(self):
        """
        Cria um sistema viário com liberdade criativa baseado nos parâmetros.
        """
        try:
            experimentacao = self.parametros.get('experimentacao_formas', 'Totalmente Livres')
            
            if experimentacao == 'Retangulares':
                self._criar_malha_retangular()
            elif experimentacao == 'Variadas':
                self._criar_malha_variada()
            elif experimentacao == 'Experimentais':
                self._criar_malha_experimental()
            else:  # Totalmente Livres
                self._criar_malha_totalmente_livre()
            
            # Criar ruas e calçadas
            self._gerar_ruas_e_calcadas()
            
            print(f"Sistema viário criativo: {len(self.ruas)} ruas, {len(self.calcadas)} calçadas")
            
        except Exception as e:
            print(f"Erro na criação do sistema viário: {e}")
            self.malha_viaria = []
            self.ruas = []
            self.calcadas = []
    
    def _criar_malha_retangular(self):
        """Cria malha viária retangular tradicional"""
        bounds = self.perimetro_internalizado.bounds
        min_x, min_y, max_x, max_y = bounds
        
        largura_total = max_x - min_x
        altura_total = max_y - min_y
        profundidade_max = self.parametros['profundidade_max_quadra']
        
        linhas_viarias = []
        
        # Linhas verticais
        num_verticais = max(1, int(largura_total / profundidade_max))
        for i in range(1, num_verticais + 1):
            x = min_x + (i * largura_total / (num_verticais + 1))
            linha = LineString([(x, min_y - 10), (x, max_y + 10)])
            intersecao = linha.intersection(self.perimetro_internalizado)
            if isinstance(intersecao, LineString) and intersecao.length > 0:
                linhas_viarias.append(intersecao)
        
        # Linhas horizontais
        num_horizontais = max(1, int(altura_total / profundidade_max))
        for i in range(1, num_horizontais + 1):
            y = min_y + (i * altura_total / (num_horizontais + 1))
            linha = LineString([(min_x - 10, y), (max_x + 10, y)])
            intersecao = linha.intersection(self.perimetro_internalizado)
            if isinstance(intersecao, LineString) and intersecao.length > 0:
                linhas_viarias.append(intersecao)
        
        self.malha_viaria = linhas_viarias
    
    def _criar_malha_variada(self):
        """Cria malha viária com variações"""
        self._criar_malha_retangular()
        
        # Adicionar algumas linhas diagonais
        bounds = self.perimetro_internalizado.bounds
        min_x, min_y, max_x, max_y = bounds
        
        # Diagonal principal
        diagonal = LineString([(min_x, min_y), (max_x, max_y)])
        intersecao = diagonal.intersection(self.perimetro_internalizado)
        if isinstance(intersecao, LineString) and intersecao.length > 0:
            self.malha_viaria.append(intersecao)
    
    def _criar_malha_experimental(self):
        """Cria malha viária experimental"""
        bounds = self.perimetro_internalizado.bounds
        min_x, min_y, max_x, max_y = bounds
        centro_x, centro_y = (min_x + max_x) / 2, (min_y + max_y) / 2
        
        linhas_viarias = []
        
        # Linhas radiais
        num_radiais = 4 + int(self.fator_criatividade * 4)
        for i in range(num_radiais):
            angulo = (2 * math.pi * i) / num_radiais
            raio = max(max_x - min_x, max_y - min_y)
            
            x_fim = centro_x + raio * math.cos(angulo)
            y_fim = centro_y + raio * math.sin(angulo)
            
            linha = LineString([(centro_x, centro_y), (x_fim, y_fim)])
            intersecao = linha.intersection(self.perimetro_internalizado)
            if isinstance(intersecao, LineString) and intersecao.length > 0:
                linhas_viarias.append(intersecao)
        
        # Linhas concêntricas
        num_concentricas = 2 + int(self.fator_criatividade * 2)
        for i in range(1, num_concentricas + 1):
            raio = (i * min(max_x - centro_x, max_y - centro_y)) / (num_concentricas + 1)
            circulo = Point(centro_x, centro_y).buffer(raio).boundary
            intersecao = circulo.intersection(self.perimetro_internalizado)
            if hasattr(intersecao, 'geoms'):
                for geom in intersecao.geoms:
                    if isinstance(geom, LineString) and geom.length > 0:
                        linhas_viarias.append(geom)
            elif isinstance(intersecao, LineString) and intersecao.length > 0:
                linhas_viarias.append(intersecao)
        
        self.malha_viaria = linhas_viarias
    
    def _criar_malha_totalmente_livre(self):
        """Cria malha viária com total liberdade criativa"""
        bounds = self.perimetro_internalizado.bounds
        min_x, min_y, max_x, max_y = bounds
        
        linhas_viarias = []
        
        # Estratégia 1: Linhas orgânicas baseadas na forma do terreno
        coords = list(self.perimetro_internalizado.exterior.coords)
        num_pontos = len(coords)
        
        # Criar linhas conectando pontos opostos
        for i in range(0, num_pontos // 2):
            ponto1 = coords[i]
            ponto2 = coords[i + num_pontos // 2] if i + num_pontos // 2 < num_pontos else coords[i - num_pontos // 2]
            
            linha = LineString([ponto1, ponto2])
            intersecao = linha.intersection(self.perimetro_internalizado)
            if isinstance(intersecao, LineString) and intersecao.length > 0:
                linhas_viarias.append(intersecao)
        
        # Estratégia 2: Linhas baseadas em pontos de interesse
        centroid = self.perimetro_internalizado.centroid
        
        # Encontrar pontos extremos
        pontos_extremos = [
            (min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y),
            (centroid.x, min_y), (centroid.x, max_y), (min_x, centroid.y), (max_x, centroid.y)
        ]
        
        for ponto in pontos_extremos:
            if self.perimetro_internalizado.contains(Point(ponto)):
                # Linha do centroide ao ponto
                linha = LineString([centroid.coords[0], ponto])
                intersecao = linha.intersection(self.perimetro_internalizado)
                if isinstance(intersecao, LineString) and intersecao.length > 0:
                    linhas_viarias.append(intersecao)
        
        # Estratégia 3: Linhas aleatórias criativas (se fator de criatividade alto)
        if self.fator_criatividade > 0.7:
            num_aleatorias = int(self.fator_criatividade * 5)
            for _ in range(num_aleatorias):
                # Pontos aleatórios dentro do perímetro
                x1 = random.uniform(min_x, max_x)
                y1 = random.uniform(min_y, max_y)
                x2 = random.uniform(min_x, max_x)
                y2 = random.uniform(min_y, max_y)
                
                if (self.perimetro_internalizado.contains(Point(x1, y1)) and 
                    self.perimetro_internalizado.contains(Point(x2, y2))):
                    
                    linha = LineString([(x1, y1), (x2, y2)])
                    intersecao = linha.intersection(self.perimetro_internalizado)
                    if isinstance(intersecao, LineString) and intersecao.length > 0:
                        linhas_viarias.append(intersecao)
        
        self.malha_viaria = linhas_viarias
    
    def _gerar_ruas_e_calcadas(self):
        """Gera ruas e calçadas a partir da malha viária"""
        if not self.malha_viaria:
            self.ruas = []
            self.calcadas = []
            return
        
        largura_rua = self.parametros['largura_rua']
        largura_calcada = self.parametros['largura_calcada']
        
        try:
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
                
        except Exception as e:
            print(f"Erro ao gerar ruas e calçadas: {e}")
            self.ruas = []
            self.calcadas = []
    
    def formar_quadras_criativas(self):
        """
        Forma quadras com liberdade criativa total.
        """
        try:
            if not self.malha_viaria:
                # Se não há malha viária, usar o perímetro como quadra única
                self.quadras = [self.perimetro_internalizado]
                return
            
            # Subtrair ruas do perímetro para formar quadras
            area_disponivel = self.perimetro_internalizado
            
            if self.ruas:
                ruas_unidas = unary_union(self.ruas)
                area_disponivel = area_disponivel.difference(ruas_unidas)
            
            # Processar resultado
            if isinstance(area_disponivel, Polygon):
                self.quadras = [area_disponivel]
            elif isinstance(area_disponivel, MultiPolygon):
                self.quadras = [geom for geom in area_disponivel.geoms if isinstance(geom, Polygon)]
            else:
                self.quadras = [self.perimetro_internalizado]
            
            # Filtrar quadras muito pequenas
            area_minima_quadra = self.parametros['area_minima_lote'] * 3
            self.quadras = [q for q in self.quadras if q.area >= area_minima_quadra]
            
            print(f"Quadras criativas formadas: {len(self.quadras)}")
            for i, quadra in enumerate(self.quadras):
                print(f"  Quadra {i+1}: {quadra.area:.2f} m²")
                
        except Exception as e:
            print(f"Erro na formação de quadras: {e}")
            self.quadras = [self.perimetro_internalizado]
    
    def subdividir_quadras_ultra_otimizado(self):
        """
        Subdivisão ultra-otimizada com foco em aproveitamento máximo e lotes de esquina.
        """
        try:
            self.lotes = []
            
            for i, quadra in enumerate(self.quadras):
                print(f"Processando quadra {i+1}: área = {quadra.area:.2f} m²")
                
                # Estratégia baseada no tamanho da quadra
                if quadra.area < self.parametros['area_minima_lote'] * 2:
                    # Quadra pequena: usar como lote único
                    if self._quadra_tem_acesso_rua(quadra):
                        self.lotes.append(quadra)
                        print(f"  Quadra {i+1} convertida em lote único")
                else:
                    # Quadra grande: subdividir otimizadamente
                    lotes_quadra = self._subdividir_quadra_otimizada(quadra, i+1)
                    self.lotes.extend(lotes_quadra)
                    print(f"  Lotes criados na quadra {i+1}: {len(lotes_quadra)}")
            
            print(f"Total de lotes criados: {len(self.lotes)}")
            
        except Exception as e:
            print(f"Erro na subdivisão ultra-otimizada: {e}")
    
    def _subdividir_quadra_otimizada(self, quadra: Polygon, numero_quadra: int) -> List[Polygon]:
        """
        Subdivide uma quadra de forma otimizada considerando:
        - Lotes de esquina com orientação otimizada
        - Máximo aproveitamento de área
        - Distribuição inteligente
        """
        lotes = []
        
        try:
            # Analisar a geometria da quadra
            analise = self._analisar_geometria_quadra(quadra)
            
            # Estratégia 1: Lotes de esquina otimizados
            lotes_esquina = self._criar_lotes_esquina_otimizados(quadra, analise)
            lotes.extend(lotes_esquina)
            
            # Calcular área restante
            if lotes_esquina:
                area_usada = unary_union(lotes_esquina)
                area_restante = quadra.difference(area_usada)
            else:
                area_restante = quadra
            
            # Estratégia 2: Lotes ao longo das bordas
            if isinstance(area_restante, Polygon) and area_restante.area > self.parametros['area_minima_lote']:
                lotes_bordas = self._criar_lotes_bordas_otimizados(area_restante, analise)
                lotes.extend(lotes_bordas)
                
                # Atualizar área restante
                if lotes_bordas:
                    area_usada_bordas = unary_union(lotes_bordas)
                    area_restante = area_restante.difference(area_usada_bordas)
            
            # Estratégia 3: Lotes no centro (se sobrar área significativa)
            if isinstance(area_restante, Polygon) and area_restante.area > self.parametros['area_minima_lote']:
                lotes_centro = self._criar_lotes_centro_adaptativos(area_restante)
                lotes.extend(lotes_centro)
            
            # Filtrar lotes muito pequenos
            lotes_validos = []
            for lote in lotes:
                if isinstance(lote, Polygon) and lote.area >= self.parametros['area_minima_lote']:
                    lotes_validos.append(lote)
            
            return lotes_validos
            
        except Exception as e:
            print(f"Erro na subdivisão otimizada da quadra {numero_quadra}: {e}")
            return []
    
    def _analisar_geometria_quadra(self, quadra: Polygon) -> Dict[str, Any]:
        """
        Analisa a geometria da quadra para otimizar a subdivisão.
        """
        bounds = quadra.bounds
        min_x, min_y, max_x, max_y = bounds
        
        largura = max_x - min_x
        altura = max_y - min_y
        area = quadra.area
        perimetro = quadra.length
        
        # Calcular compacidade (relação área/perímetro)
        compacidade = (4 * math.pi * area) / (perimetro ** 2)
        
        # Identificar orientação principal
        if largura > altura * 1.5:
            orientacao = 'horizontal'
        elif altura > largura * 1.5:
            orientacao = 'vertical'
        else:
            orientacao = 'quadrada'
        
        # Encontrar cantos/esquinas
        coords = list(quadra.exterior.coords)[:-1]
        esquinas = self._identificar_esquinas(coords)
        
        return {
            'largura': largura,
            'altura': altura,
            'area': area,
            'perimetro': perimetro,
            'compacidade': compacidade,
            'orientacao': orientacao,
            'esquinas': esquinas,
            'coords': coords,
            'bounds': bounds
        }
    
    def _identificar_esquinas(self, coords: List[Tuple[float, float]]) -> List[Dict[str, Any]]:
        """
        Identifica esquinas e suas características.
        """
        esquinas = []
        n = len(coords)
        
        for i in range(n):
            p1 = coords[i-1]
            p2 = coords[i]
            p3 = coords[(i+1) % n]
            
            # Calcular ângulo
            v1 = (p1[0] - p2[0], p1[1] - p2[1])
            v2 = (p3[0] - p2[0], p3[1] - p2[1])
            
            # Produto escalar e magnitudes
            dot_product = v1[0] * v2[0] + v1[1] * v2[1]
            mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
            mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
            
            if mag1 > 0 and mag2 > 0:
                cos_angle = dot_product / (mag1 * mag2)
                cos_angle = max(-1, min(1, cos_angle))  # Clamp para evitar erros
                angulo = math.acos(cos_angle)
                angulo_graus = math.degrees(angulo)
                
                # Considerar como esquina se o ângulo for significativo
                if angulo_graus < 150:  # Ângulo menor que 150° é considerado esquina
                    esquinas.append({
                        'ponto': p2,
                        'angulo': angulo_graus,
                        'indice': i,
                        'tipo': 'convexa' if angulo_graus < 90 else 'suave'
                    })
        
        return esquinas
    
    def _criar_lotes_esquina_otimizados(self, quadra: Polygon, analise: Dict[str, Any]) -> List[Polygon]:
        """
        Cria lotes de esquina com orientação otimizada.
        """
        lotes_esquina = []
        estrategia = self.parametros.get('estrategia_esquina', 'Automático')
        
        try:
            esquinas = analise['esquinas']
            
            for esquina in esquinas:
                if esquina['angulo'] < 120:  # Apenas esquinas bem definidas
                    lote_esquina = self._criar_lote_esquina_individual(quadra, esquina, estrategia, analise)
                    if lote_esquina:
                        lotes_esquina.append(lote_esquina)
            
            return lotes_esquina
            
        except Exception as e:
            print(f"Erro ao criar lotes de esquina: {e}")
            return []
    
    def _criar_lote_esquina_individual(self, quadra: Polygon, esquina: Dict[str, Any], 
                                     estrategia: str, analise: Dict[str, Any]) -> Optional[Polygon]:
        """
        Cria um lote de esquina individual otimizado.
        """
        try:
            ponto_esquina = esquina['ponto']
            coords = analise['coords']
            indice = esquina['indice']
            
            # Determinar dimensões do lote de esquina
            if estrategia == 'Testada Maior':
                testada = self.parametros['testada_maxima_lote']
                profundidade = self.parametros['profundidade_minima_lote']
            elif estrategia == 'Testada Menor':
                testada = self.parametros['testada_minima_lote']
                profundidade = self.parametros['profundidade_maxima_lote']
            elif estrategia == 'Área Maior':
                testada = self.parametros['testada_preferencial_lote']
                profundidade = self.parametros['profundidade_maxima_lote']
            else:  # Automático
                testada = self.parametros['testada_preferencial_lote']
                profundidade = self.parametros['profundidade_padrao_lote']
            
            # Criar lote retangular na esquina
            n = len(coords)
            p_anterior = coords[indice-1]
            p_atual = ponto_esquina
            p_proximo = coords[(indice+1) % n]
            
            # Vetores das bordas
            v1 = (p_anterior[0] - p_atual[0], p_anterior[1] - p_atual[1])
            v2 = (p_proximo[0] - p_atual[0], p_proximo[1] - p_atual[1])
            
            # Normalizar vetores
            mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
            mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
            
            if mag1 > 0 and mag2 > 0:
                v1_norm = (v1[0]/mag1, v1[1]/mag1)
                v2_norm = (v2[0]/mag2, v2[1]/mag2)
                
                # Pontos do lote de esquina
                p1 = p_atual
                p2 = (p_atual[0] + testada * v1_norm[0], p_atual[1] + testada * v1_norm[1])
                p3 = (p2[0] + profundidade * v2_norm[0], p2[1] + profundidade * v2_norm[1])
                p4 = (p_atual[0] + profundidade * v2_norm[0], p_atual[1] + profundidade * v2_norm[1])
                
                lote_tentativa = Polygon([p1, p2, p3, p4])
                
                # Intersectar com a quadra
                lote_final = lote_tentativa.intersection(quadra)
                
                if isinstance(lote_final, Polygon) and lote_final.area >= self.parametros['area_minima_lote']:
                    return lote_final
            
            return None
            
        except Exception as e:
            print(f"Erro ao criar lote de esquina individual: {e}")
            return None
    
    def _criar_lotes_bordas_otimizados(self, area_restante: Polygon, analise: Dict[str, Any]) -> List[Polygon]:
        """
        Cria lotes otimizados ao longo das bordas.
        """
        lotes_bordas = []
        
        try:
            # Encontrar bordas com acesso à rua
            bordas_com_rua = self._encontrar_bordas_com_rua(area_restante)
            
            for borda in bordas_com_rua:
                lotes_borda = self._subdividir_borda_inteligente(area_restante, borda)
                lotes_bordas.extend(lotes_borda)
            
            return lotes_bordas
            
        except Exception as e:
            print(f"Erro ao criar lotes de bordas: {e}")
            return []
    
    def _subdividir_borda_inteligente(self, area: Polygon, borda: LineString) -> List[Polygon]:
        """
        Subdivide uma borda de forma inteligente.
        """
        lotes = []
        
        try:
            comprimento_borda = borda.length
            
            # Calcular número ótimo de lotes
            testada_preferencial = self.parametros['testada_preferencial_lote']
            num_lotes_ideal = max(1, int(comprimento_borda / testada_preferencial))
            
            # Ajustar baseado na densidade desejada
            num_lotes_final = int(num_lotes_ideal * self.fator_densidade)
            num_lotes_final = max(1, num_lotes_final)
            
            largura_lote = comprimento_borda / num_lotes_final
            
            # Criar lotes ao longo da borda
            for i in range(num_lotes_final):
                inicio_norm = i / num_lotes_final
                fim_norm = (i + 1) / num_lotes_final
                
                lote = self._criar_lote_ao_longo_borda(area, borda, inicio_norm, fim_norm, largura_lote)
                if lote and lote.area >= self.parametros['area_minima_lote']:
                    lotes.append(lote)
            
            return lotes
            
        except Exception as e:
            print(f"Erro na subdivisão inteligente de borda: {e}")
            return []
    
    def _criar_lote_ao_longo_borda(self, area: Polygon, borda: LineString, 
                                  inicio_norm: float, fim_norm: float, largura: float) -> Optional[Polygon]:
        """
        Cria um lote ao longo de uma borda específica.
        """
        try:
            # Pontos ao longo da borda
            p1 = borda.interpolate(inicio_norm, normalized=True)
            p2 = borda.interpolate(fim_norm, normalized=True)
            
            # Vetor da borda
            dx = p2.x - p1.x
            dy = p2.y - p1.y
            
            # Vetor perpendicular (para dentro da área)
            perp_x = -dy
            perp_y = dx
            
            # Normalizar
            mag = math.sqrt(perp_x**2 + perp_y**2)
            if mag > 0:
                perp_x /= mag
                perp_y /= mag
            
            # Determinar profundidade adaptativa
            profundidade_max = self.parametros['profundidade_maxima_lote']
            profundidade_min = self.parametros['profundidade_minima_lote']
            
            # Tentar diferentes profundidades
            for fator in [1.0, 0.8, 0.6, 1.2, 1.5]:
                profundidade = min(profundidade_max, profundidade_min * fator)
                
                # Criar retângulo
                pontos = [
                    (p1.x, p1.y),
                    (p2.x, p2.y),
                    (p2.x + perp_x * profundidade, p2.y + perp_y * profundidade),
                    (p1.x + perp_x * profundidade, p1.y + perp_y * profundidade)
                ]
                
                lote_tentativa = Polygon(pontos)
                lote_final = lote_tentativa.intersection(area)
                
                if isinstance(lote_final, Polygon) and lote_final.area >= self.parametros['area_minima_lote']:
                    return lote_final
            
            return None
            
        except Exception as e:
            print(f"Erro ao criar lote ao longo da borda: {e}")
            return None
    
    def _criar_lotes_centro_adaptativos(self, area_restante: Polygon) -> List[Polygon]:
        """
        Cria lotes adaptativos no centro da área restante.
        """
        lotes_centro = []
        
        try:
            if area_restante.area < self.parametros['area_minima_lote'] * 2:
                # Área pequena: usar como lote único
                if area_restante.area >= self.parametros['area_minima_lote']:
                    lotes_centro.append(area_restante)
                return lotes_centro
            
            # Estratégia baseada na forma da área
            bounds = area_restante.bounds
            min_x, min_y, max_x, max_y = bounds
            largura = max_x - min_x
            altura = max_y - min_y
            
            if largura > altura * 2:
                # Área alongada horizontalmente: dividir verticalmente
                lotes_centro = self._dividir_verticalmente(area_restante)
            elif altura > largura * 2:
                # Área alongada verticalmente: dividir horizontalmente
                lotes_centro = self._dividir_horizontalmente(area_restante)
            else:
                # Área aproximadamente quadrada: usar triangulação
                lotes_centro = self._triangular_area_adaptativa(area_restante)
            
            return lotes_centro
            
        except Exception as e:
            print(f"Erro ao criar lotes centro adaptativos: {e}")
            return []
    
    def _dividir_verticalmente(self, area: Polygon) -> List[Polygon]:
        """Divide área verticalmente"""
        lotes = []
        bounds = area.bounds
        min_x, min_y, max_x, max_y = bounds
        
        largura_total = max_x - min_x
        testada_preferencial = self.parametros['testada_preferencial_lote']
        
        num_divisoes = max(1, int(largura_total / testada_preferencial))
        largura_divisao = largura_total / num_divisoes
        
        for i in range(num_divisoes):
            x = min_x + i * largura_divisao
            linha_corte = LineString([(x, min_y - 10), (x, max_y + 10)])
            
            if i == 0:
                # Primeira divisão
                x_fim = min_x + largura_divisao
                linha_fim = LineString([(x_fim, min_y - 10), (x_fim, max_y + 10)])
                
                # Criar polígono da divisão
                pontos_divisao = [
                    (min_x, min_y), (x_fim, min_y), (x_fim, max_y), (min_x, max_y)
                ]
                divisao = Polygon(pontos_divisao)
                lote = divisao.intersection(area)
                
                if isinstance(lote, Polygon) and lote.area >= self.parametros['area_minima_lote']:
                    lotes.append(lote)
            else:
                # Divisões intermediárias
                x_inicio = min_x + (i-1) * largura_divisao
                x_fim = min_x + i * largura_divisao
                
                pontos_divisao = [
                    (x_inicio, min_y), (x_fim, min_y), (x_fim, max_y), (x_inicio, max_y)
                ]
                divisao = Polygon(pontos_divisao)
                lote = divisao.intersection(area)
                
                if isinstance(lote, Polygon) and lote.area >= self.parametros['area_minima_lote']:
                    lotes.append(lote)
        
        return lotes
    
    def _dividir_horizontalmente(self, area: Polygon) -> List[Polygon]:
        """Divide área horizontalmente"""
        lotes = []
        bounds = area.bounds
        min_x, min_y, max_x, max_y = bounds
        
        altura_total = max_y - min_y
        profundidade_preferencial = self.parametros['profundidade_padrao_lote']
        
        num_divisoes = max(1, int(altura_total / profundidade_preferencial))
        altura_divisao = altura_total / num_divisoes
        
        for i in range(num_divisoes):
            y_inicio = min_y + i * altura_divisao
            y_fim = min_y + (i + 1) * altura_divisao
            
            pontos_divisao = [
                (min_x, y_inicio), (max_x, y_inicio), (max_x, y_fim), (min_x, y_fim)
            ]
            divisao = Polygon(pontos_divisao)
            lote = divisao.intersection(area)
            
            if isinstance(lote, Polygon) and lote.area >= self.parametros['area_minima_lote']:
                lotes.append(lote)
        
        return lotes
    
    def _triangular_area_adaptativa(self, area: Polygon) -> List[Polygon]:
        """Triangula área de forma adaptativa"""
        lotes = []
        
        try:
            coords = list(area.exterior.coords)[:-1]
            
            if len(coords) <= 4:
                # Polígono simples: dividir por diagonais
                if len(coords) == 4:
                    # Quadrilátero: dividir em 2 triângulos
                    triangulo1 = Polygon([coords[0], coords[1], coords[2]])
                    triangulo2 = Polygon([coords[0], coords[2], coords[3]])
                    
                    if triangulo1.area >= self.parametros['area_minima_lote']:
                        lotes.append(triangulo1)
                    if triangulo2.area >= self.parametros['area_minima_lote']:
                        lotes.append(triangulo2)
                else:
                    # Triângulo: usar como está se for grande o suficiente
                    if area.area >= self.parametros['area_minima_lote']:
                        lotes.append(area)
            else:
                # Polígono complexo: usar centroide para dividir
                centroide = area.centroid
                
                for i in range(len(coords)):
                    p1 = coords[i]
                    p2 = coords[(i + 1) % len(coords)]
                    
                    triangulo = Polygon([p1, p2, centroide.coords[0]])
                    triangulo_intersecao = triangulo.intersection(area)
                    
                    if isinstance(triangulo_intersecao, Polygon) and triangulo_intersecao.area >= self.parametros['area_minima_lote']:
                        lotes.append(triangulo_intersecao)
            
            return lotes
            
        except Exception as e:
            print(f"Erro na triangulação adaptativa: {e}")
            return [area] if area.area >= self.parametros['area_minima_lote'] else []
    
    def _quadra_tem_acesso_rua(self, quadra: Polygon) -> bool:
        """Verifica se a quadra tem acesso direto à rua"""
        try:
            for rua in self.ruas:
                if quadra.distance(rua) < 2.0:
                    return True
            return False
        except:
            return False
    
    def _encontrar_bordas_com_rua(self, area: Polygon) -> List[LineString]:
        """Encontra bordas da área que fazem interface com ruas"""
        bordas_com_rua = []
        
        try:
            # Converter perímetro em segmentos
            coords = list(area.exterior.coords)
            
            for i in range(len(coords) - 1):
                segmento = LineString([coords[i], coords[i + 1]])
                
                # Verificar se o segmento está próximo de alguma rua
                tem_acesso = False
                for rua in self.ruas:
                    if segmento.distance(rua) < 5.0:  # Tolerância de 5 metros
                        tem_acesso = True
                        break
                
                if tem_acesso:
                    bordas_com_rua.append(segmento)
            
            return bordas_com_rua
            
        except Exception as e:
            print(f"Erro ao encontrar bordas com rua: {e}")
            return []
    
    def alocar_areas_comuns_estrategicamente(self):
        """
        Aloca áreas comuns de forma estratégica.
        """
        try:
            area_total = self.perimetro_original.area
            percentual_verde = self.parametros['percentual_area_verde']
            percentual_institucional = self.parametros['percentual_area_institucional']
            
            area_verde_necessaria = (percentual_verde / 100) * area_total
            area_institucional_necessaria = (percentual_institucional / 100) * area_total
            
            print(f"Área verde necessária: {area_verde_necessaria:.2f} m² ({percentual_verde}%)")
            print(f"Área institucional necessária: {area_institucional_necessaria:.2f} m² ({percentual_institucional}%)")
            
            # Encontrar áreas disponíveis para áreas comuns
            areas_disponiveis = self._encontrar_areas_para_areas_comuns()
            
            # Alocar áreas verdes
            self.areas_verdes = self._alocar_areas_verdes(areas_disponiveis, area_verde_necessaria)
            
            # Alocar áreas institucionais
            self.areas_institucionais = self._alocar_areas_institucionais(areas_disponiveis, area_institucional_necessaria)
            
            area_verde_total = sum(area.area for area in self.areas_verdes)
            area_institucional_total = sum(area.area for area in self.areas_institucionais)
            
            print(f"Áreas verdes alocadas: {len(self.areas_verdes)} ({area_verde_total:.2f} m²)")
            print(f"Áreas institucionais alocadas: {len(self.areas_institucionais)} ({area_institucional_total:.2f} m²)")
            
        except Exception as e:
            print(f"Erro na alocação de áreas comuns: {e}")
            self.areas_verdes = []
            self.areas_institucionais = []
    
    def _encontrar_areas_para_areas_comuns(self) -> List[Polygon]:
        """Encontra áreas disponíveis para áreas comuns"""
        areas_disponiveis = []
        
        try:
            # Área total disponível
            area_total = self.perimetro_internalizado
            
            # Subtrair ruas
            if self.ruas:
                ruas_unidas = unary_union(self.ruas)
                area_total = area_total.difference(ruas_unidas)
            
            # Subtrair lotes
            if self.lotes:
                lotes_unidos = unary_union(self.lotes)
                area_restante = area_total.difference(lotes_unidos)
                
                if isinstance(area_restante, Polygon):
                    areas_disponiveis.append(area_restante)
                elif isinstance(area_restante, MultiPolygon):
                    areas_disponiveis.extend([geom for geom in area_restante.geoms if isinstance(geom, Polygon)])
            
            # Filtrar áreas muito pequenas
            area_minima = self.parametros['area_minima_lote'] * 0.5
            areas_disponiveis = [area for area in areas_disponiveis if area.area >= area_minima]
            
            return areas_disponiveis
            
        except Exception as e:
            print(f"Erro ao encontrar áreas para áreas comuns: {e}")
            return []
    
    def _alocar_areas_verdes(self, areas_disponiveis: List[Polygon], area_necessaria: float) -> List[Polygon]:
        """Aloca áreas verdes"""
        areas_verdes = []
        area_alocada = 0
        
        # Ordenar áreas por tamanho (maiores primeiro)
        areas_ordenadas = sorted(areas_disponiveis, key=lambda x: x.area, reverse=True)
        
        for area in areas_ordenadas:
            if area_alocada >= area_necessaria:
                break
            
            areas_verdes.append(area)
            area_alocada += area.area
        
        return areas_verdes
    
    def _alocar_areas_institucionais(self, areas_disponiveis: List[Polygon], area_necessaria: float) -> List[Polygon]:
        """Aloca áreas institucionais"""
        areas_institucionais = []
        
        # Para áreas institucionais, usar áreas menores que não foram usadas para verde
        areas_usadas_verde = set(id(area) for area in self.areas_verdes)
        areas_restantes = [area for area in areas_disponiveis if id(area) not in areas_usadas_verde]
        
        area_alocada = 0
        for area in areas_restantes:
            if area_alocada >= area_necessaria:
                break
            
            areas_institucionais.append(area)
            area_alocada += area.area
        
        return areas_institucionais
    
    def calcular_estatisticas_detalhadas(self) -> Dict[str, float]:
        """Calcula estatísticas detalhadas do loteamento"""
        try:
            area_total = self.perimetro_original.area
            num_lotes = len(self.lotes)
            
            area_lotes = sum(lote.area for lote in self.lotes)
            area_ruas = sum(rua.area for rua in self.ruas)
            area_calcadas = sum(calcada.area for calcada in self.calcadas)
            area_verde = sum(area.area for area in self.areas_verdes)
            area_institucional = sum(area.area for area in self.areas_institucionais)
            
            return {
                'area_total': area_total,
                'num_lotes': num_lotes,
                'area_lotes': area_lotes,
                'area_ruas': area_ruas,
                'area_calcadas': area_calcadas,
                'area_verde': area_verde,
                'area_institucional': area_institucional
            }
            
        except Exception as e:
            print(f"Erro ao calcular estatísticas: {e}")
            return {
                'area_total': 0,
                'num_lotes': 0,
                'area_lotes': 0,
                'area_ruas': 0,
                'area_calcadas': 0,
                'area_verde': 0,
                'area_institucional': 0
            }
    
    def exportar_dxf_ultra_avancado(self, arquivo_saida: str):
        """
        Exporta o resultado em formato DXF com organização ultra-avançada.
        """
        try:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            # Criar layers organizados
            layers = {
                'PERIMETRO': {'color': 1, 'linetype': 'CONTINUOUS'},  # Vermelho
                'RUAS': {'color': 2, 'linetype': 'CONTINUOUS'},       # Amarelo
                'CALCADAS': {'color': 8, 'linetype': 'CONTINUOUS'},   # Cinza
                'QUADRAS': {'color': 3, 'linetype': 'DASHED'},        # Verde
                'LOTES': {'color': 4, 'linetype': 'CONTINUOUS'},      # Ciano
                'AREA_VERDE': {'color': 3, 'linetype': 'CONTINUOUS'}, # Verde
                'AREA_INST': {'color': 6, 'linetype': 'CONTINUOUS'},  # Magenta
                'MALHA_VIARIA': {'color': 7, 'linetype': 'CENTER'}    # Branco
            }
            
            for layer_name, props in layers.items():
                layer = doc.layers.new(layer_name)
                layer.color = props['color']
                layer.linetype = props['linetype']
            
            # Adicionar perímetro original
            if self.perimetro_original:
                coords = list(self.perimetro_original.exterior.coords)
                msp.add_lwpolyline(coords, dxfattribs={'layer': 'PERIMETRO'})
            
            # Adicionar malha viária
            for linha in self.malha_viaria:
                coords = list(linha.coords)
                msp.add_lwpolyline(coords, dxfattribs={'layer': 'MALHA_VIARIA'})
            
            # Adicionar ruas
            for rua in self.ruas:
                coords = list(rua.exterior.coords)
                msp.add_lwpolyline(coords, dxfattribs={'layer': 'RUAS'})
            
            # Adicionar calçadas
            for calcada in self.calcadas:
                coords = list(calcada.exterior.coords)
                msp.add_lwpolyline(coords, dxfattribs={'layer': 'CALCADAS'})
            
            # Adicionar quadras
            for quadra in self.quadras:
                coords = list(quadra.exterior.coords)
                msp.add_lwpolyline(coords, dxfattribs={'layer': 'QUADRAS'})
            
            # Adicionar lotes
            for lote in self.lotes:
                coords = list(lote.exterior.coords)
                msp.add_lwpolyline(coords, dxfattribs={'layer': 'LOTES'})
            
            # Adicionar áreas verdes
            for area in self.areas_verdes:
                coords = list(area.exterior.coords)
                msp.add_lwpolyline(coords, dxfattribs={'layer': 'AREA_VERDE'})
            
            # Adicionar áreas institucionais
            for area in self.areas_institucionais:
                coords = list(area.exterior.coords)
                msp.add_lwpolyline(coords, dxfattribs={'layer': 'AREA_INST'})
            
            # Salvar arquivo
            doc.saveas(arquivo_saida)
            print(f"Arquivo DXF ultra-avançado salvo: {arquivo_saida}")
            
        except Exception as e:
            print(f"Erro ao exportar DXF: {e}")

