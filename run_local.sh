#!/bin/bash
# Script para executar o app localmente

# Configurar variáveis de ambiente para modo local
export USE_GCS=false
export DATASET_FILE=test_dataset.csv
export THEMES_FILE=themes_tree_enriched_full.yaml

# Executar Streamlit
streamlit run app/main.py
