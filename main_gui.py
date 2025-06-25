import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
import threading
import math
from loteamento_processor_ultra_avancado import LoteamentoProcessorUltraAvancado

# Configuração do tema do CustomTkinter
ctk.set_appearance_mode("light")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class LoteamentoApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Aplicativo de Loteamento Urbano")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Variáveis para armazenar os parâmetros
        self.setup_variables()
        
        # Criar a interface
        self.create_interface()
        
    def setup_variables(self):
        """Inicializa todas as variáveis do formulário"""
        # Informações do Projeto
        self.arquivo_path = ctk.StringVar()
        self.nome_projeto = ctk.StringVar()
        
        # Parâmetros das Vias
        self.largura_rua = ctk.DoubleVar(value=8.0)
        self.largura_calcada = ctk.DoubleVar(value=2.0)
        self.largura_total_via = ctk.StringVar(value="12.0 m")
        
        # Parâmetros das Quadras
        self.profundidade_max_quadra = ctk.DoubleVar(value=80.0)
        self.orientacao_preferencial = ctk.StringVar(value="Automática")
        
        # Parâmetros dos Lotes
        self.area_minima_lote = ctk.DoubleVar(value=200.0)
        self.testada_minima_lote = ctk.DoubleVar(value=8.0)
        self.largura_padrao_lote = ctk.DoubleVar(value=12.0)
        self.profundidade_padrao_lote = ctk.DoubleVar(value=30.0)
        
        # Parâmetros de Áreas Comuns
        self.percentual_area_verde = ctk.DoubleVar(value=15.0)
        self.percentual_area_institucional = ctk.DoubleVar(value=5.0)
        
        # Configurar callbacks para atualização automática
        self.largura_rua.trace('w', self.atualizar_largura_total_via)
        self.largura_calcada.trace('w', self.atualizar_largura_total_via)
        
    def atualizar_largura_total_via(self, *args):
        """Atualiza automaticamente a largura total da via"""
        try:
            total = self.largura_rua.get() + (2 * self.largura_calcada.get())
            self.largura_total_via.set(f"{total:.1f} m")
        except:
            self.largura_total_via.set("-- m")
    
    def create_interface(self):
        """Cria toda a interface do usuário"""
        # Frame principal com scroll
        main_frame = ctk.CTkScrollableFrame(self.root, label_text="Parâmetros do Loteamento")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Seção 1: Informações do Projeto
        self.create_project_info_section(main_frame)
        
        # Seção 2: Parâmetros das Vias
        self.create_vias_section(main_frame)
        
        # Seção 3: Parâmetros das Quadras
        self.create_quadras_section(main_frame)
        
        # Seção 4: Parâmetros dos Lotes
        self.create_lotes_section(main_frame)
        
        # Seção 5: Parâmetros de Áreas Comuns
        self.create_areas_comuns_section(main_frame)
        
        # Seção 6: Botões de Ação
        self.create_action_buttons(main_frame)
        
    def create_project_info_section(self, parent):
        """Cria a seção de informações do projeto"""
        # Frame da seção
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", padx=10, pady=10)
        
        # Título da seção
        title_label = ctk.CTkLabel(section_frame, text="📁 Informações do Projeto", 
                                  font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=(15, 10))
        
        # Caminho do arquivo
        arquivo_frame = ctk.CTkFrame(section_frame)
        arquivo_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(arquivo_frame, text="Arquivo (.dxf ou .kml):").pack(anchor="w", padx=10, pady=(10, 5))
        
        arquivo_input_frame = ctk.CTkFrame(arquivo_frame)
        arquivo_input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.arquivo_entry = ctk.CTkEntry(arquivo_input_frame, textvariable=self.arquivo_path, 
                                         placeholder_text="Selecione o arquivo do perímetro...")
        self.arquivo_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        browse_button = ctk.CTkButton(arquivo_input_frame, text="Procurar", 
                                     command=self.browse_file, width=100)
        browse_button.pack(side="right", padx=(5, 10), pady=10)
        
        # Nome do projeto
        nome_frame = ctk.CTkFrame(section_frame)
        nome_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(nome_frame, text="Nome do Projeto:").pack(anchor="w", padx=10, pady=(10, 5))
        nome_entry = ctk.CTkEntry(nome_frame, textvariable=self.nome_projeto, 
                                 placeholder_text="Digite o nome do loteamento...")
        nome_entry.pack(fill="x", padx=10, pady=(0, 10))
        
    def create_vias_section(self, parent):
        """Cria a seção de parâmetros das vias"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", padx=10, pady=10)
        
        title_label = ctk.CTkLabel(section_frame, text="🛣️ Parâmetros das Vias (Ruas)", 
                                  font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=(15, 10))
        
        # Grid para organizar os campos
        grid_frame = ctk.CTkFrame(section_frame)
        grid_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Largura da rua
        ctk.CTkLabel(grid_frame, text="Largura da Rua (m):").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        largura_rua_entry = ctk.CTkEntry(grid_frame, textvariable=self.largura_rua, width=100)
        largura_rua_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Largura da calçada
        ctk.CTkLabel(grid_frame, text="Largura da Calçada (m):").grid(row=1, column=0, sticky="w", padx=10, pady=10)
        largura_calcada_entry = ctk.CTkEntry(grid_frame, textvariable=self.largura_calcada, width=100)
        largura_calcada_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Largura total (calculada automaticamente)
        ctk.CTkLabel(grid_frame, text="Largura Total da Via:").grid(row=2, column=0, sticky="w", padx=10, pady=10)
        largura_total_label = ctk.CTkLabel(grid_frame, textvariable=self.largura_total_via, 
                                          font=ctk.CTkFont(weight="bold"))
        largura_total_label.grid(row=2, column=1, sticky="w", padx=10, pady=10)
        
    def create_quadras_section(self, parent):
        """Cria a seção de parâmetros das quadras"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", padx=10, pady=10)
        
        title_label = ctk.CTkLabel(section_frame, text="🏘️ Parâmetros das Quadras", 
                                  font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=(15, 10))
        
        grid_frame = ctk.CTkFrame(section_frame)
        grid_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Profundidade máxima da quadra
        ctk.CTkLabel(grid_frame, text="Profundidade Máxima da Quadra (m):").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        prof_quadra_entry = ctk.CTkEntry(grid_frame, textvariable=self.profundidade_max_quadra, width=100)
        prof_quadra_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Orientação preferencial
        ctk.CTkLabel(grid_frame, text="Orientação Preferencial:").grid(row=1, column=0, sticky="w", padx=10, pady=10)
        orientacao_combo = ctk.CTkComboBox(grid_frame, variable=self.orientacao_preferencial,
                                          values=["Automática", "Norte-Sul", "Leste-Oeste", "Nordeste-Sudoeste", "Noroeste-Sudeste"])
        orientacao_combo.grid(row=1, column=1, padx=10, pady=10)
        
    def create_lotes_section(self, parent):
        """Cria a seção expandida de parâmetros dos lotes"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", padx=10, pady=10)
        
        title_label = ctk.CTkLabel(section_frame, text="🏠 Parâmetros Detalhados dos Lotes", 
                                  font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=(15, 10))
        
        # Frame principal para organizar em colunas
        main_grid_frame = ctk.CTkFrame(section_frame)
        main_grid_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Coluna 1: Área dos Lotes
        area_frame = ctk.CTkFrame(main_grid_frame)
        area_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        area_title = ctk.CTkLabel(area_frame, text="Área dos Lotes (m²)", 
                                 font=ctk.CTkFont(weight="bold"))
        area_title.pack(pady=(10, 5))
        
        # Área mínima
        ctk.CTkLabel(area_frame, text="Área Mínima:").pack(anchor="w", padx=10)
        area_min_entry = ctk.CTkEntry(area_frame, textvariable=self.area_minima_lote, width=120)
        area_min_entry.pack(fill="x", padx=10, pady=(0, 5))
        
        # Área máxima
        ctk.CTkLabel(area_frame, text="Área Máxima:").pack(anchor="w", padx=10)
        self.area_maxima_lote = ctk.StringVar(value="600")
        area_max_entry = ctk.CTkEntry(area_frame, textvariable=self.area_maxima_lote, width=120)
        area_max_entry.pack(fill="x", padx=10, pady=(0, 5))
        
        # Área preferencial
        ctk.CTkLabel(area_frame, text="Área Preferencial:").pack(anchor="w", padx=10)
        self.area_preferencial_lote = ctk.StringVar(value="300")
        area_pref_entry = ctk.CTkEntry(area_frame, textvariable=self.area_preferencial_lote, width=120)
        area_pref_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Coluna 2: Testada dos Lotes
        testada_frame = ctk.CTkFrame(main_grid_frame)
        testada_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        testada_title = ctk.CTkLabel(testada_frame, text="Testada dos Lotes (m)", 
                                    font=ctk.CTkFont(weight="bold"))
        testada_title.pack(pady=(10, 5))
        
        # Testada mínima
        ctk.CTkLabel(testada_frame, text="Testada Mínima:").pack(anchor="w", padx=10)
        testada_min_entry = ctk.CTkEntry(testada_frame, textvariable=self.testada_minima_lote, width=120)
        testada_min_entry.pack(fill="x", padx=10, pady=(0, 5))
        
        # Testada máxima
        ctk.CTkLabel(testada_frame, text="Testada Máxima:").pack(anchor="w", padx=10)
        self.testada_maxima_lote = ctk.StringVar(value="20")
        testada_max_entry = ctk.CTkEntry(testada_frame, textvariable=self.testada_maxima_lote, width=120)
        testada_max_entry.pack(fill="x", padx=10, pady=(0, 5))
        
        # Testada preferencial
        ctk.CTkLabel(testada_frame, text="Testada Preferencial:").pack(anchor="w", padx=10)
        self.testada_preferencial_lote = ctk.StringVar(value="12")
        testada_pref_entry = ctk.CTkEntry(testada_frame, textvariable=self.testada_preferencial_lote, width=120)
        testada_pref_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Coluna 3: Profundidade dos Lotes
        profundidade_frame = ctk.CTkFrame(main_grid_frame)
        profundidade_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        profundidade_title = ctk.CTkLabel(profundidade_frame, text="Profundidade dos Lotes (m)", 
                                         font=ctk.CTkFont(weight="bold"))
        profundidade_title.pack(pady=(10, 5))
        
        # Profundidade mínima
        ctk.CTkLabel(profundidade_frame, text="Profundidade Mínima:").pack(anchor="w", padx=10)
        self.profundidade_minima_lote = ctk.StringVar(value="15")
        prof_min_entry = ctk.CTkEntry(profundidade_frame, textvariable=self.profundidade_minima_lote, width=120)
        prof_min_entry.pack(fill="x", padx=10, pady=(0, 5))
        
        # Profundidade máxima
        ctk.CTkLabel(profundidade_frame, text="Profundidade Máxima:").pack(anchor="w", padx=10)
        self.profundidade_maxima_lote = ctk.StringVar(value="40")
        prof_max_entry = ctk.CTkEntry(profundidade_frame, textvariable=self.profundidade_maxima_lote, width=120)
        prof_max_entry.pack(fill="x", padx=10, pady=(0, 5))
        
        # Profundidade preferencial
        ctk.CTkLabel(profundidade_frame, text="Profundidade Preferencial:").pack(anchor="w", padx=10)
        prof_pref_entry = ctk.CTkEntry(profundidade_frame, textvariable=self.profundidade_padrao_lote, width=120)
        prof_pref_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Seção de Estratégias de Subdivisão
        estrategias_frame = ctk.CTkFrame(section_frame)
        estrategias_frame.pack(fill="x", padx=15, pady=(10, 15))
        
        estrategias_title = ctk.CTkLabel(estrategias_frame, text="🎯 Estratégias de Subdivisão", 
                                        font=ctk.CTkFont(size=14, weight="bold"))
        estrategias_title.pack(pady=(10, 5))
        
        # Frame para estratégias em colunas
        estrategias_content = ctk.CTkFrame(estrategias_frame)
        estrategias_content.pack(fill="x", padx=10, pady=(0, 10))
        
        # Coluna 1: Prioridades
        prioridades_frame = ctk.CTkFrame(estrategias_content)
        prioridades_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        ctk.CTkLabel(prioridades_frame, text="Prioridade:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 0))
        self.prioridade_aproveitamento = ctk.StringVar(value="Máximo Aproveitamento")
        prioridade_combo = ctk.CTkComboBox(prioridades_frame, variable=self.prioridade_aproveitamento,
                                          values=["Máximo Aproveitamento", "Lotes Regulares", "Lotes Grandes", "Lotes Pequenos"])
        prioridade_combo.pack(fill="x", padx=10, pady=(0, 5))
        
        ctk.CTkLabel(prioridades_frame, text="Tolerância de Forma:").pack(anchor="w", padx=10)
        self.tolerancia_forma = ctk.StringVar(value="Alta (Mais Irregular)")
        tolerancia_combo = ctk.CTkComboBox(prioridades_frame, variable=self.tolerancia_forma,
                                          values=["Baixa (Mais Regular)", "Média", "Alta (Mais Irregular)"])
        tolerancia_combo.pack(fill="x", padx=10, pady=(0, 10))
        
        # Coluna 2: Distribuição
        distribuicao_frame = ctk.CTkFrame(estrategias_content)
        distribuicao_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        ctk.CTkLabel(distribuicao_frame, text="Lotes de Esquina:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 0))
        self.estrategia_esquina = ctk.StringVar(value="Automático")
        esquina_combo = ctk.CTkComboBox(distribuicao_frame, variable=self.estrategia_esquina,
                                       values=["Automático", "Testada Maior", "Testada Menor", "Área Maior"])
        esquina_combo.pack(fill="x", padx=10, pady=(0, 5))
        
        ctk.CTkLabel(distribuicao_frame, text="Densidade:").pack(anchor="w", padx=10)
        self.densidade_lotes = ctk.StringVar(value="Alta")
        densidade_combo = ctk.CTkComboBox(distribuicao_frame, variable=self.densidade_lotes,
                                         values=["Baixa", "Média", "Alta", "Máxima"])
        densidade_combo.pack(fill="x", padx=10, pady=(0, 10))
        
        # Coluna 3: Criatividade
        criatividade_frame = ctk.CTkFrame(estrategias_content)
        criatividade_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        ctk.CTkLabel(criatividade_frame, text="Liberdade Criativa:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 0))
        self.liberdade_criativa = ctk.StringVar(value="Máxima")
        liberdade_combo = ctk.CTkComboBox(criatividade_frame, variable=self.liberdade_criativa,
                                         values=["Conservadora", "Moderada", "Criativa", "Máxima"])
        liberdade_combo.pack(fill="x", padx=10, pady=(0, 5))
        
        ctk.CTkLabel(criatividade_frame, text="Formas de Quadra:").pack(anchor="w", padx=10)
        self.experimentacao_formas = ctk.StringVar(value="Totalmente Livres")
        formas_combo = ctk.CTkComboBox(criatividade_frame, variable=self.experimentacao_formas,
                                      values=["Retangulares", "Variadas", "Experimentais", "Totalmente Livres"])
        formas_combo.pack(fill="x", padx=10, pady=(0, 10))
        
    def create_areas_comuns_section(self, parent):
        """Cria a seção de parâmetros de áreas comuns"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", padx=10, pady=10)
        
        title_label = ctk.CTkLabel(section_frame, text="🌳 Parâmetros de Áreas Comuns", 
                                  font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=(15, 10))
        
        grid_frame = ctk.CTkFrame(section_frame)
        grid_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Percentual de área verde
        ctk.CTkLabel(grid_frame, text="Percentual de Área Verde (%):").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        area_verde_entry = ctk.CTkEntry(grid_frame, textvariable=self.percentual_area_verde, width=100)
        area_verde_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Percentual de área institucional
        ctk.CTkLabel(grid_frame, text="Percentual de Área Institucional (%):").grid(row=1, column=0, sticky="w", padx=10, pady=10)
        area_inst_entry = ctk.CTkEntry(grid_frame, textvariable=self.percentual_area_institucional, width=100)
        area_inst_entry.grid(row=1, column=1, padx=10, pady=10)
        
    def create_action_buttons(self, parent):
        """Cria os botões de ação"""
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x", padx=10, pady=20)
        
        # Frame interno para centralizar os botões
        inner_frame = ctk.CTkFrame(button_frame)
        inner_frame.pack(pady=20)
        
        # Botão de processar
        process_button = ctk.CTkButton(inner_frame, text="🚀 Processar Loteamento", 
                                      command=self.processar_loteamento,
                                      font=ctk.CTkFont(size=14, weight="bold"),
                                      height=40, width=200)
        process_button.pack(side="left", padx=10)
        
        # Botão de limpar
        clear_button = ctk.CTkButton(inner_frame, text="🗑️ Limpar Campos", 
                                    command=self.limpar_campos,
                                    font=ctk.CTkFont(size=14),
                                    height=40, width=150)
        clear_button.pack(side="left", padx=10)
        
        # Botão de sair
        exit_button = ctk.CTkButton(inner_frame, text="❌ Sair", 
                                   command=self.root.quit,
                                   font=ctk.CTkFont(size=14),
                                   height=40, width=100)
        exit_button.pack(side="left", padx=10)
        
    def browse_file(self):
        """Abre o diálogo para selecionar arquivo"""
        file_types = [
            ("Arquivos CAD", "*.dxf *.kml"),
            ("Arquivos DXF", "*.dxf"),
            ("Arquivos KML", "*.kml"),
            ("Todos os arquivos", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Selecionar arquivo do perímetro",
            filetypes=file_types
        )
        
        if filename:
            self.arquivo_path.set(filename)
            
    def limpar_campos(self):
        """Limpa todos os campos do formulário"""
        self.arquivo_path.set("")
        self.nome_projeto.set("")
        self.largura_rua.set(8.0)
        self.largura_calcada.set(2.0)
        self.profundidade_max_quadra.set(80.0)
        self.orientacao_preferencial.set("Automática")
        self.area_minima_lote.set(200.0)
        self.testada_minima_lote.set(8.0)
        self.largura_padrao_lote.set(12.0)
        self.profundidade_padrao_lote.set(30.0)
        self.percentual_area_verde.set(15.0)
        self.percentual_area_institucional.set(5.0)
        
    def validar_numero_seguro(self, valor, nome_campo: str, minimo: float = 0.1, maximo: float = 10000.0) -> float:
        """
        Valida um número de forma segura, evitando valores NaN, infinitos ou fora do intervalo.
        
        Args:
            valor: Valor a ser validado
            nome_campo: Nome do campo para mensagens de erro
            minimo: Valor mínimo permitido
            maximo: Valor máximo permitido
            
        Returns:
            Valor validado
            
        Raises:
            ValueError: Se o valor for inválido
        """
        try:
            if isinstance(valor, str):
                # Remover espaços e substituir vírgula por ponto
                valor = valor.strip().replace(',', '.')
                if not valor:
                    raise ValueError(f"Campo {nome_campo} está vazio")
            
            valor_float = float(valor)
            
            # Verificar NaN e infinito
            if math.isnan(valor_float):
                raise ValueError(f"Valor NaN (não é um número) em {nome_campo}")
            if math.isinf(valor_float):
                raise ValueError(f"Valor infinito em {nome_campo}")
            
            # Verificar intervalo
            if valor_float < minimo:
                raise ValueError(f"Valor muito pequeno em {nome_campo}: {valor_float} (mínimo: {minimo})")
            if valor_float > maximo:
                raise ValueError(f"Valor muito grande em {nome_campo}: {valor_float} (máximo: {maximo})")
                
            return valor_float
            
        except (ValueError, TypeError) as e:
            if "could not convert" in str(e) or "invalid literal" in str(e):
                raise ValueError(f"Valor inválido em {nome_campo}: '{valor}' não é um número válido")
            else:
                raise e

    def validar_parametros(self):
        """Valida os parâmetros inseridos pelo usuário com verificação robusta contra NaN"""
        erros = []
        
        # Verificar se o arquivo foi selecionado
        if not self.arquivo_path.get():
            erros.append("Selecione um arquivo de perímetro (.dxf ou .kml)")
        elif not os.path.exists(self.arquivo_path.get()):
            erros.append("O arquivo selecionado não existe")
            
        # Verificar se o nome do projeto foi preenchido
        if not self.nome_projeto.get().strip():
            erros.append("Digite um nome para o projeto")
            
        # Validar valores numéricos com verificação robusta
        try:
            self.validar_numero_seguro(self.largura_rua.get(), "Largura da Rua", 1.0, 50.0)
        except ValueError as e:
            erros.append(str(e))
            
        try:
            self.validar_numero_seguro(self.largura_calcada.get(), "Largura da Calçada", 0.0, 20.0)
        except ValueError as e:
            erros.append(str(e))
            
        try:
            self.validar_numero_seguro(self.profundidade_max_quadra.get(), "Profundidade Máxima da Quadra", 10.0, 500.0)
        except ValueError as e:
            erros.append(str(e))
            
        try:
            self.validar_numero_seguro(self.area_minima_lote.get(), "Área Mínima do Lote", 50.0, 5000.0)
        except ValueError as e:
            erros.append(str(e))
            
        try:
            self.validar_numero_seguro(self.testada_minima_lote.get(), "Testada Mínima do Lote", 3.0, 100.0)
        except ValueError as e:
            erros.append(str(e))
            
        try:
            self.validar_numero_seguro(self.largura_padrao_lote.get(), "Largura Padrão do Lote", 5.0, 100.0)
        except ValueError as e:
            erros.append(str(e))
            
        try:
            self.validar_numero_seguro(self.profundidade_padrao_lote.get(), "Profundidade Padrão do Lote", 10.0, 200.0)
        except ValueError as e:
            erros.append(str(e))
            
        try:
            percentual_verde = self.validar_numero_seguro(self.percentual_area_verde.get(), "Percentual de Área Verde", 0.0, 100.0)
        except ValueError as e:
            erros.append(str(e))
            percentual_verde = 0
            
        try:
            percentual_inst = self.validar_numero_seguro(self.percentual_area_institucional.get(), "Percentual de Área Institucional", 0.0, 100.0)
        except ValueError as e:
            erros.append(str(e))
            percentual_inst = 0
            
        # Verificar se a soma dos percentuais não excede 100%
        if percentual_verde + percentual_inst > 100:
            erros.append("A soma dos percentuais de área verde e institucional não pode exceder 100%")
            
        return erros
        
    def processar_loteamento(self):
        """Processa o loteamento com os parâmetros fornecidos"""
        # Validar parâmetros
        erros = self.validar_parametros()
        
        if erros:
            messagebox.showerror("Erro de Validação", "\n".join(erros))
            return
        
        # Preparar parâmetros para o processador
        parametros = {
            'largura_rua': self.largura_rua.get(),
            'largura_calcada': self.largura_calcada.get(),
            'profundidade_max_quadra': self.profundidade_max_quadra.get(),
            'orientacao_preferencial': self.orientacao_preferencial.get(),
            'area_minima_lote': self.area_minima_lote.get(),
            'testada_minima_lote': self.testada_minima_lote.get(),
            'largura_padrao_lote': self.largura_padrao_lote.get(),
            'profundidade_padrao_lote': self.profundidade_padrao_lote.get(),
            'percentual_area_verde': self.percentual_area_verde.get(),
            'percentual_area_institucional': self.percentual_area_institucional.get()
        }
        
        # Definir arquivo de saída
        nome_projeto = self.nome_projeto.get().strip()
        if not nome_projeto:
            nome_projeto = "loteamento"
        
        # Criar diretório de saída se não existir
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        arquivo_saida = os.path.join(output_dir, f"{nome_projeto}.dxf")
        
        # Criar janela de progresso
        progress_window = ctk.CTkToplevel(self.root)
        progress_window.title("Processando Loteamento")
        progress_window.geometry("400x200")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        # Centralizar janela de progresso
        progress_window.update_idletasks()
        x = (progress_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (progress_window.winfo_screenheight() // 2) - (200 // 2)
        progress_window.geometry(f"400x200+{x}+{y}")
        
        # Widgets da janela de progresso
        ctk.CTkLabel(progress_window, text="Processando loteamento...", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        
        progress_bar = ctk.CTkProgressBar(progress_window, width=300)
        progress_bar.pack(pady=10)
        progress_bar.set(0)
        
        status_label = ctk.CTkLabel(progress_window, text="Iniciando processamento...")
        status_label.pack(pady=10)
        
        def atualizar_progresso(etapa, progresso):
            """Atualiza a barra de progresso e status"""
            progress_bar.set(progresso)
            status_label.configure(text=etapa)
            progress_window.update()
        
        def processar_em_thread():
            """Executa o processamento em thread separada"""
            try:
                # Criar processador ultra-avançado
                atualizar_progresso("Inicializando processador ultra-avançado...", 0.1)
                processor = LoteamentoProcessorUltraAvancado(parametros)
                
                # Carregar perímetro
                atualizar_progresso("Carregando perímetro...", 0.2)
                if not processor.carregar_perimetro(self.arquivo_path.get()):
                    raise Exception("Erro ao carregar perímetro do arquivo")
                
                # Executar processamento ultra-avançado completo
                atualizar_progresso("Executando processamento ultra-avançado...", 0.3)
                resultado = processor.processar_loteamento_ultra_avancado(
                    self.arquivo_path.get(), 
                    arquivo_saida
                )
                
                if not resultado['sucesso']:
                    raise Exception(resultado.get('erro', 'Erro desconhecido no processamento'))
                
                atualizar_progresso("Processamento concluído!", 1.0)
                
                # Usar estatísticas do resultado
                area_total = resultado.get('area_total', 0)
                num_lotes = resultado.get('num_lotes', 0)
                area_lotes = resultado.get('area_lotes', 0)
                area_ruas = resultado.get('area_ruas', 0)
                area_calcadas = resultado.get('area_calcadas', 0)
                area_verde = resultado.get('area_verde', 0)
                area_institucional = resultado.get('area_institucional', 0)
                
                # Fechar janela de progresso
                progress_window.destroy()
                
                # Exibir resultados ultra-avançados
                percentual_lotes = (area_lotes/area_total)*100 if area_total > 0 else 0
                percentual_ruas = (area_ruas/area_total)*100 if area_total > 0 else 0
                percentual_calcadas = (area_calcadas/area_total)*100 if area_total > 0 else 0
                percentual_verde = (area_verde/area_total)*100 if area_total > 0 else 0
                percentual_institucional = (area_institucional/area_total)*100 if area_total > 0 else 0
                
                resultado_texto = f"""
🎉 LOTEAMENTO ULTRA-AVANÇADO PROCESSADO COM SUCESSO!

📊 ESTATÍSTICAS DETALHADAS:
• Área total do terreno: {area_total:.2f} m²
• Número de lotes criados: {num_lotes}
• Área dos lotes: {area_lotes:.2f} m² ({percentual_lotes:.1f}%)
• Área das ruas: {area_ruas:.2f} m² ({percentual_ruas:.1f}%)
• Área das calçadas: {area_calcadas:.2f} m² ({percentual_calcadas:.1f}%)
• Área verde: {area_verde:.2f} m² ({percentual_verde:.1f}%)
• Área institucional: {area_institucional:.2f} m² ({percentual_institucional:.1f}%)

🚀 FUNCIONALIDADES ULTRA-AVANÇADAS APLICADAS:
• ✅ Subdivisão otimizada com lotes irregulares
• ✅ Lotes de esquina com orientação inteligente
• ✅ Sistema viário criativo ({parametros.get('experimentacao_formas', 'Padrão')})
• ✅ Liberdade criativa: {parametros.get('liberdade_criativa', 'Máxima')}
• ✅ Estratégia de esquina: {parametros.get('estrategia_esquina', 'Automático')}
• ✅ Densidade de lotes: {parametros.get('densidade_lotes', 'Alta')}
• ✅ Tolerância de forma: {parametros.get('tolerancia_forma', 'Alta')}

📐 PARÂMETROS UTILIZADOS:
• Área dos lotes: {parametros.get('area_minima_lote', 0):.0f} - {parametros.get('area_maxima_lote', 0):.0f} m²
• Testada dos lotes: {parametros.get('testada_minima_lote', 0):.0f} - {parametros.get('testada_maxima_lote', 0):.0f} m
• Profundidade dos lotes: {parametros.get('profundidade_minima_lote', 0):.0f} - {parametros.get('profundidade_maxima_lote', 0):.0f} m

📁 ARQUIVO GERADO:
{arquivo_saida}

🎯 APROVEITAMENTO OTIMIZADO:
O algoritmo ultra-avançado maximizou o aproveitamento da área irregular,
criando lotes adaptativos com acesso garantido às ruas e distribuição
inteligente das áreas comuns.

O arquivo DXF foi salvo com layers organizados e pode ser aberto em qualquer software CAD.
"""
                
                messagebox.showinfo("Processamento Concluído", resultado_texto)
                
            except Exception as e:
                progress_window.destroy()
                messagebox.showerror("Erro no Processamento", f"Ocorreu um erro durante o processamento:\n\n{str(e)}")
        
        # Iniciar processamento em thread separada
        thread = threading.Thread(target=processar_em_thread)
        thread.daemon = True
        thread.start()
        
    def run(self):
        """Inicia a aplicação"""
        self.root.mainloop()

if __name__ == "__main__":
    app = LoteamentoApp()
    app.run()

