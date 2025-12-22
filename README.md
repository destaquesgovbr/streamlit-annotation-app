# Anotação de Notícias GovBR - Fase 4.3

Aplicação Streamlit para anotação manual de notícias governamentais brasileiras com classificação temática hierárquica (L1 → L2 → L3).

## 📋 Funcionalidades

- ✅ Interface web intuitiva para anotação
- ✅ Navegação sequencial (anterior/próxima)
- ✅ Seleção hierárquica de temas (L1 → L2 → L3)
- ✅ Nível de confiança (alta/média/baixa)
- ✅ Filtros por status e complexidade
- ✅ Progresso em tempo real
- ✅ Suporte a múltiplos anotadores
- ✅ Visualização de ground truth original
- ✅ Persistência automática (local ou GCS)

## 🚀 Uso Local

### Pré-requisitos

- Python 3.11+
- pip

### Instalação

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Prepare os dados:
   ```bash
   # Copiar arquivos necessários para data/
   cp ../data/test_dataset.csv data/
   cp ../../themes_tree_enriched_full.yaml data/
   ```

3. Execute o app:
   ```bash
   streamlit run app/main.py
   ```

4. Acesse `http://localhost:8501` no navegador

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# Usar Google Cloud Storage (default: false)
export USE_GCS=false

# Nome do bucket GCS (se USE_GCS=true)
export GCS_BUCKET=dgb-streamlit-data

# Nome do arquivo de dataset (default: test_dataset.csv)
export DATASET_FILE=test_dataset.csv

# Nome do arquivo da árvore temática (default: themes_tree_enriched_full.yaml)
export THEMES_FILE=themes_tree_enriched_full.yaml
```

### Modo Local (padrão)

Por padrão, o app usa arquivos locais em `data/`:
- `data/test_dataset.csv` - Dataset de notícias para anotação
- `data/themes_tree_enriched_full.yaml` - Árvore temática

### Modo GCS (para deploy)

Quando `USE_GCS=true`, o app:
- Lê/escreve dados no Google Cloud Storage
- Usa autenticação via Application Default Credentials
- Bucket configurável via `GCS_BUCKET`

## 🐳 Docker

### Build local

```bash
docker build -t annotation-app .
```

### Run local

```bash
docker run -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  annotation-app
```

## 📊 Estrutura de Dados

### Dataset (CSV)

Colunas necessárias:
- `unique_id`: ID único da notícia
- `titulo`: Título da notícia
- `resumo`: Resumo (opcional)
- `conteudo_inicio`: Primeiros 500 caracteres do conteúdo
- `orgao`: Órgão emissor
- `data_publicacao`: Data de publicação
- `url`: Link original (opcional)
- `complexidade_estimada`: clara/moderada/dificil
- `L1_anotado`, `L2_anotado`, `L3_anotado`: Classificação anotada
- `confianca`: Nível de confiança
- `observacoes`: Observações do anotador
- `anotador`: Nome do anotador
- `data_anotacao`: Timestamp da anotação
- `L1_original`, `L2_original`, `L3_original`: Ground truth original

### Árvore Temática (YAML)

Estrutura hierárquica:
```yaml
themes:
  - code: "01"
    label: "Economia e Finanças"
    description: "..."
    keywords: [...]
    children:
      - code: "01.01"
        label: "Política Econômica"
        children:
          - code: "01.01.01"
            label: "Política Fiscal"
            # ...
```

## 🎨 Interface

### Sidebar
- **Progresso**: Total, anotadas, pendentes
- **Filtros**: Por status (todas/pendentes/anotadas) e complexidade

### Área Principal
- **Navegação**: Botões anterior/próxima
- **Conteúdo**: Título, resumo, início do conteúdo
- **Formulário**: Seleção hierárquica L1→L2→L3, confiança, observações
- **Ground Truth**: Visualização da classificação original (expansível)

## 📝 Guia de Anotação

Consulte [reports/03_classification_guide.md](../reports/03_classification_guide.md) para:
- Regras de classificação
- Casos especiais
- Exemplos práticos
- Checklist de qualidade

## 🔄 Workflow de Anotação

1. **Ler** título, resumo e (se necessário) conteúdo
2. **Identificar** tema principal (L1)
3. **Selecionar** subtema (L2) e categoria (L3)
4. **Avaliar** confiança na classificação
5. **Documentar** observações para casos ambíguos
6. **Salvar** anotação
7. Ir para **próxima** notícia

## 🚢 Deploy no GCP

### 1. Preparar dados no GCS

```bash
# Upload dataset
gsutil cp data/test_dataset.csv gs://dgb-streamlit-data/

# Upload árvore temática
gsutil cp data/themes_tree_enriched_full.yaml gs://dgb-streamlit-data/
```

### 2. Configurar app para GCS

Edite `.streamlit/config.toml` ou use variáveis de ambiente:
```bash
USE_GCS=true
GCS_BUCKET=dgb-streamlit-data
```

### 3. Seguir processo de deploy DGB

Consulte [streamlit-boilerplate README](https://github.com/destaquesgovbr/streamlit-boilerplate) para:
- Registrar app na plataforma
- Configurar secrets do GitHub
- Deploy automático via GitHub Actions

## 🧪 Testes

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Rodar testes (quando implementados)
pytest
```

## 📁 Estrutura do Projeto

```
streamlit-annotation-app/
├── app/
│   ├── main.py                  # Aplicação principal
│   └── utils/
│       ├── data_loader.py       # Carregamento de dados (local/GCS)
│       └── theme_hierarchy.py   # Utilitários para árvore temática
├── data/
│   ├── test_dataset.csv        # Dataset de notícias
│   └── themes_tree_enriched_full.yaml  # Árvore temática
├── .streamlit/
│   └── config.toml             # Configuração do Streamlit
├── .streamlit-app.yaml         # Metadados para catálogo DGB
├── Dockerfile                  # Container definition
├── requirements.txt            # Dependências Python
├── .gitignore
├── .dockerignore
└── README.md
```

## 🆘 Troubleshooting

### Erro: "Arquivo não encontrado"
- Certifique-se que os arquivos estão em `data/`
- Verifique nomes dos arquivos (case-sensitive)
- Se usando GCS, verifique permissões do bucket

### Erro: "Cannot save dataset"
- Modo local: verifique permissões de escrita em `data/`
- Modo GCS: verifique service account permissions

### App não carrega dados
- Verifique formato do CSV (encoding UTF-8)
- Verifique formato do YAML (sintaxe válida)
- Veja logs no terminal para detalhes

## 📞 Suporte

Para problemas ou dúvidas:
1. Consulte documentação da [Fase 4](../README.md)
2. Veja [guia de classificação](../reports/03_classification_guide.md)
3. Abra issue no repositório

## 📄 Licença

Projeto interno - DestaquesGovBr
