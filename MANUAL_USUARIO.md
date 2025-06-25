# Manual do Usuário - Aplicativo de Loteamento Urbano

## Índice

1. [Introdução](#introdução)
2. [Instalação](#instalação)
3. [Primeiros Passos](#primeiros-passos)
4. [Interface do Usuário](#interface-do-usuário)
5. [Configuração de Parâmetros](#configuração-de-parâmetros)
6. [Processamento](#processamento)
7. [Resultados](#resultados)
8. [Integração com CAD](#integração-com-cad)
9. [Solução de Problemas](#solução-de-problemas)
10. [Suporte Técnico](#suporte-técnico)

## Introdução

O Aplicativo de Loteamento Urbano é uma ferramenta especializada para análise e subdivisão automática de perímetros de terrenos. Desenvolvido com tecnologias modernas, oferece uma interface intuitiva similar ao AutoCAD/Civil 3D, permitindo a criação eficiente de loteamentos urbanos completos.

### Características Principais

- **Interface Moderna**: Desenvolvida com CustomTkinter para uma experiência visual profissional
- **Algoritmo Inteligente**: Implementa heurísticas avançadas para otimização do desenho urbano
- **Compatibilidade CAD**: Importa arquivos .dxf e .kml, exporta resultados em .dxf
- **Configuração Flexível**: Permite ajuste detalhado de todos os parâmetros de loteamento
- **Processamento Geoespacial**: Utiliza bibliotecas especializadas para cálculos precisos

## Instalação

### Requisitos do Sistema

- **Sistema Operacional**: Windows 10/11, Linux Ubuntu 18.04+, ou macOS 10.14+
- **Python**: Versão 3.8 ou superior
- **Memória RAM**: Mínimo 4GB, recomendado 8GB
- **Espaço em Disco**: 500MB livres

### Instalação Automática

1. Descompacte o arquivo do aplicativo em uma pasta de sua escolha
2. Execute o arquivo `instalar.py`:
   ```
   python instalar.py
   ```
3. Aguarde a instalação automática das dependências
4. Siga as instruções na tela

### Instalação Manual

Se preferir instalar manualmente:

```bash
pip install customtkinter geopandas shapely ezdxf
```

## Primeiros Passos

### 1. Executando o Aplicativo

Execute o arquivo principal:
```
python loteamento_app.py
```

### 2. Preparando Arquivos de Entrada

O aplicativo aceita dois tipos de arquivo:

- **Arquivos DXF**: Devem conter uma polilinha fechada representando o perímetro
- **Arquivos KML**: Devem conter um polígono representando o perímetro

### 3. Arquivos de Teste

O aplicativo inclui arquivos de teste na pasta `assets/`:
- `perimetro_retangular.dxf`: Terreno retangular simples (100m x 80m)
- `perimetro_irregular.dxf`: Terreno com forma irregular
- `perimetro_complexo.dxf`: Terreno em forma de "L"

## Interface do Usuário

A interface está organizada em seções lógicas para facilitar a configuração:

### Seção 1: Informações do Projeto
- **Arquivo**: Botão para selecionar o arquivo de perímetro
- **Nome do Projeto**: Campo para identificar o loteamento

### Seção 2: Parâmetros das Vias
- **Largura da Rua**: Largura do leito carroçável
- **Largura da Calçada**: Largura de cada calçada
- **Largura Total**: Calculada automaticamente

### Seção 3: Parâmetros das Quadras
- **Profundidade Máxima**: Limite para evitar quadras muito longas
- **Orientação Preferencial**: Direção do arruamento

### Seção 4: Parâmetros dos Lotes
- **Área Mínima**: Área mínima permitida por lote
- **Testada Mínima**: Largura mínima da frente do lote
- **Dimensões Padrão**: Largura e profundidade ideais

### Seção 5: Áreas Comuns
- **Área Verde**: Percentual para parques e praças
- **Área Institucional**: Percentual para equipamentos públicos

## Configuração de Parâmetros

### Parâmetros das Vias

**Largura da Rua (metros)**
- Valor típico: 6-12 metros
- Considera apenas o leito carroçável
- Não inclui calçadas

**Largura da Calçada (metros)**
- Valor típico: 1.5-3 metros
- Aplicada em ambos os lados da rua
- A largura total da via é calculada automaticamente

### Parâmetros das Quadras

**Profundidade Máxima da Quadra (metros)**
- Valor típico: 60-120 metros
- Evita quadras excessivamente longas
- Influencia diretamente o número de quadras

**Orientação Preferencial**
- **Automática**: O algoritmo determina a melhor orientação
- **Norte-Sul**: Força orientação vertical
- **Leste-Oeste**: Força orientação horizontal
- **Nordeste-Sudoeste**: Orientação diagonal
- **Noroeste-Sudeste**: Orientação diagonal oposta

### Parâmetros dos Lotes

**Área Mínima do Lote (m²)**
- Geralmente definida pelo plano diretor municipal
- Valores típicos: 125-500 m²
- Nenhum lote será criado abaixo deste valor

**Testada Mínima do Lote (metros)**
- Largura mínima da frente do lote
- Valores típicos: 5-15 metros
- Garante acesso adequado ao lote

**Dimensões Padrão**
- **Largura**: Largura ideal do lote (8-20 metros)
- **Profundidade**: Profundidade ideal do lote (20-40 metros)
- O algoritmo tentará criar lotes próximos a essas dimensões

### Áreas Comuns

**Percentual de Área Verde (%)**
- Geralmente exigido por lei (10-20%)
- Destinado a parques, praças e jardins
- Calculado sobre a área total do terreno

**Percentual de Área Institucional (%)**
- Geralmente exigido por lei (5-10%)
- Destinado a escolas, postos de saúde, etc.
- Calculado sobre a área total do terreno

## Processamento

### Iniciando o Processamento

1. Configure todos os parâmetros necessários
2. Clique no botão "🚀 Processar Loteamento"
3. Aguarde a conclusão do processamento

### Etapas do Algoritmo

O processamento segue 8 etapas principais:

1. **Carregamento do Perímetro**: Leitura do arquivo de entrada
2. **Internalização**: Criação de vias perimetrais
3. **Definição do Eixo Principal**: Orientação do arruamento
4. **Criação da Malha Viária**: Rede de ruas internas
5. **Divisão em Quadras**: Subdivisão do terreno
6. **Subdivisão em Lotes**: Criação dos lotes individuais
7. **Alocação de Áreas Comuns**: Distribuição de áreas verdes e institucionais
8. **Exportação**: Geração do arquivo DXF final

### Monitoramento do Progresso

Durante o processamento, uma janela de progresso exibe:
- Barra de progresso visual
- Descrição da etapa atual
- Tempo estimado restante

## Resultados

### Arquivo DXF Gerado

O resultado é salvo como arquivo DXF na pasta `output/` com as seguintes camadas:

- **PERIMETRO** (Vermelho): Perímetro original do terreno
- **RUAS** (Amarelo): Sistema viário completo
- **QUADRAS** (Verde): Divisão em quadras
- **LOTES** (Ciano): Lotes individuais
- **AREA_VERDE** (Azul): Áreas verdes (parques, praças)
- **AREA_INST** (Magenta): Áreas institucionais

### Estatísticas do Resultado

Após o processamento, são exibidas estatísticas detalhadas:

- **Área Total**: Área do terreno original
- **Número de Lotes**: Quantidade de lotes criados
- **Área dos Lotes**: Área total e percentual dos lotes
- **Área das Ruas**: Área total e percentual do sistema viário
- **Área Verde**: Área total e percentual das áreas verdes
- **Área Institucional**: Área total e percentual das áreas institucionais
- **Área Média por Lote**: Tamanho médio dos lotes

### Abrindo o Resultado em CAD

O arquivo DXF pode ser aberto em qualquer software CAD:

1. **AutoCAD**: File → Open → Selecionar o arquivo .dxf
2. **Civil 3D**: File → Open → Selecionar o arquivo .dxf
3. **QGIS**: Layer → Add Layer → Add Vector Layer
4. **FreeCAD**: File → Open → Selecionar o arquivo .dxf

## Integração com CAD

### Script para AutoCAD (IronPython)

```python
import subprocess
import os

def processar_loteamento():
    # Exportar perímetro selecionado
    # ... código para exportar geometria ...
    
    # Executar aplicativo externo
    app_path = r"C:\caminho\para\loteamento_app.py"
    subprocess.call(['python', app_path])
    
    # Importar resultado
    # ... código para importar DXF gerado ...
```

### Fluxo de Trabalho Integrado

1. **No CAD**: Desenhar ou importar o perímetro do terreno
2. **Exportar**: Salvar como arquivo DXF
3. **Processar**: Executar o aplicativo de loteamento
4. **Importar**: Carregar o resultado de volta no CAD
5. **Refinar**: Fazer ajustes manuais se necessário

## Solução de Problemas

### Problemas Comuns

**Erro: "Dependências não encontradas"**
- Solução: Execute o script `instalar.py` novamente
- Verifique se o Python 3.8+ está instalado

**Erro: "Arquivo não pode ser carregado"**
- Verifique se o arquivo DXF contém uma polilinha fechada
- Certifique-se de que o arquivo KML contém um polígono válido
- Teste com os arquivos de exemplo fornecidos

**Nenhum lote foi criado**
- Reduza a área mínima do lote
- Reduza a testada mínima do lote
- Aumente a profundidade máxima da quadra
- Verifique se o terreno é grande o suficiente

**Poucos lotes foram criados**
- Ajuste as dimensões padrão dos lotes
- Reduza a largura das ruas e calçadas
- Verifique os percentuais de áreas comuns

**Interface não aparece**
- Verifique se o CustomTkinter foi instalado corretamente
- Execute: `pip install customtkinter --upgrade`
- Reinicie o aplicativo

### Validação de Parâmetros

O aplicativo valida automaticamente:
- Valores numéricos positivos
- Percentuais entre 0 e 100
- Soma de percentuais não excedendo 100%
- Existência do arquivo de entrada

### Logs de Erro

Em caso de erro, verifique:
- Mensagens de erro na tela
- Console do Python para detalhes técnicos
- Arquivo de log (se disponível)

## Suporte Técnico

### Informações do Sistema

Para suporte, forneça:
- Versão do Python
- Sistema operacional
- Parâmetros utilizados
- Arquivo de entrada (se possível)
- Mensagem de erro completa

### Limitações Conhecidas

- Terrenos muito irregulares podem requerer ajustes manuais
- O algoritmo é heurístico, não garante resultado "perfeito"
- Arquivos DXF muito complexos podem não ser lidos corretamente
- Terrenos muito pequenos podem não gerar lotes

### Melhorias Futuras

- Suporte a mais formatos de arquivo
- Interface 3D para visualização
- Algoritmos de otimização mais avançados
- Integração direta com softwares CAD
- Relatórios em PDF

### Contato

Para suporte técnico ou sugestões:
- Desenvolvido conforme especificações do cliente
- Código-fonte disponível para customizações
- Documentação técnica completa incluída

---

**Versão do Manual**: 1.0  
**Data**: Junho 2025  
**Aplicativo**: Loteamento Urbano v1.0

