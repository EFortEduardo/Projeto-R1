# Aplicativo de Loteamento Urbano

## Descrição

Este aplicativo foi desenvolvido para análise e subdivisão automática de perímetros de terrenos, gerando loteamentos urbanos completos com lotes, quadras, ruas e áreas comuns. O software foi projetado com uma interface intuitiva similar ao AutoCAD/Civil 3D, facilitando o uso por profissionais da área.

## Características Principais

- **Interface Gráfica Moderna**: Desenvolvida com CustomTkinter para uma experiência visual profissional
- **Algoritmo Inteligente**: Implementa heurísticas avançadas para otimização do desenho urbano
- **Compatibilidade CAD**: Importa arquivos .dxf e .kml, exporta resultados em .dxf
- **Configuração Flexível**: Permite ajuste de todos os parâmetros de loteamento
- **Processamento Geoespacial**: Utiliza GeoPandas e Shapely para cálculos precisos

## Tecnologias Utilizadas

- **Python 3.x**: Linguagem principal
- **CustomTkinter**: Interface gráfica moderna
- **GeoPandas**: Análise geoespacial
- **Shapely**: Operações geométricas
- **ezdxf**: Manipulação de arquivos DXF

## Instalação

### Pré-requisitos

- Python 3.8 ou superior
- Sistema operacional: Windows, Linux ou macOS

### Dependências

```bash
pip install customtkinter geopandas shapely ezdxf
```

## Como Usar

### 1. Executar o Aplicativo

```bash
python loteamento_app.py
```

### 2. Configurar Parâmetros

#### Informações do Projeto
- **Arquivo**: Selecione um arquivo .dxf ou .kml contendo o perímetro do terreno
- **Nome do Projeto**: Digite um nome para identificar o loteamento

#### Parâmetros das Vias
- **Largura da Rua**: Largura do leito carroçável (metros)
- **Largura da Calçada**: Largura de cada calçada (metros)
- A largura total da via é calculada automaticamente

#### Parâmetros das Quadras
- **Profundidade Máxima**: Limite para evitar quadras excessivamente longas
- **Orientação Preferencial**: Direção do arruamento (automática ou manual)

#### Parâmetros dos Lotes
- **Área Mínima**: Área mínima permitida por lote (m²)
- **Testada Mínima**: Largura mínima da frente do lote (metros)
- **Dimensões Padrão**: Largura e profundidade ideais para os lotes

#### Áreas Comuns
- **Área Verde**: Percentual destinado a parques e praças
- **Área Institucional**: Percentual para equipamentos públicos

### 3. Processar Loteamento

Clique em "Processar Loteamento" para executar o algoritmo. O progresso será exibido em tempo real.

### 4. Resultado

O aplicativo gera um arquivo .dxf com as seguintes camadas:
- **PERIMETRO**: Perímetro original do terreno
- **RUAS**: Sistema viário
- **QUADRAS**: Divisão em quadras
- **LOTES**: Lotes individuais
- **AREA_VERDE**: Áreas verdes
- **AREA_INST**: Áreas institucionais

## Algoritmo de Loteamento

O aplicativo implementa um algoritmo em 7 etapas:

1. **Internalização do Perímetro**: Criação de vias perimetrais
2. **Definição do Eixo Principal**: Orientação natural do terreno
3. **Criação da Malha Viária**: Rede de ruas internas
4. **Divisão em Quadras**: Subdivisão do terreno
5. **Subdivisão em Lotes**: Criação dos lotes individuais
6. **Alocação de Áreas Comuns**: Distribuição de áreas verdes e institucionais
7. **Exportação**: Geração do arquivo DXF final

## Arquivos de Teste

O aplicativo inclui arquivos de teste na pasta `assets/`:
- `perimetro_retangular.dxf`: Terreno retangular simples
- `perimetro_irregular.dxf`: Terreno com forma irregular
- `perimetro_complexo.dxf`: Terreno em forma de "L"

## Estrutura do Projeto

```
loteamento_app/
├── loteamento_app.py          # Executável principal
├── src/
│   ├── main_gui.py            # Interface gráfica
│   ├── loteamento_processor.py # Algoritmo de processamento
│   └── criar_arquivos_teste.py # Gerador de arquivos teste
├── assets/                    # Arquivos de teste
├── output/                    # Arquivos DXF gerados
└── README.md                  # Este arquivo
```

## Integração com CAD

### Para AutoCAD/Civil 3D

O aplicativo pode ser integrado com softwares CAD através de scripts IronPython:

1. Exportar perímetro selecionado do CAD
2. Executar o aplicativo Python externo
3. Importar o resultado de volta ao CAD

### Exemplo de Script IronPython

```python
import subprocess
import os

# Exportar perímetro selecionado
# ... código para exportar geometria ...

# Executar aplicativo externo
subprocess.call(['python', 'loteamento_app.py', 'perimetro.dxf'])

# Importar resultado
# ... código para importar DXF gerado ...
```

## Limitações e Considerações

- O algoritmo é heurístico, buscando um "bom" resultado, não necessariamente "perfeito"
- Terrenos muito irregulares podem requerer ajustes manuais
- A qualidade do resultado depende dos parâmetros fornecidos
- Recomenda-se validação dos resultados conforme normas locais

## Suporte e Desenvolvimento

Este aplicativo foi desenvolvido conforme especificações técnicas detalhadas, implementando as melhores práticas de desenvolvimento Python e processamento geoespacial.

Para melhorias ou customizações, o código está estruturado de forma modular, facilitando manutenção e extensões futuras.

## Licença

Desenvolvido sob demanda conforme plano de desenvolvimento fornecido.

