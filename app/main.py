"""
Interface de Anotação Manual de Notícias - Fase 4.3

Aplicação Streamlit para anotação manual de notícias com classificação temática.
"""

import os
import random
import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

from utils.data_loader import DataLoader
from utils.theme_hierarchy import get_theme_hierarchy, get_level
from utils.agencies import AgencyLoader


# Configuração da página
st.set_page_config(
    page_title="Anotação de Notícias GovBR - Fase 4",
    page_icon="📋",
    layout="wide"
)

# Emojis para complexidade
COMPLEXITY_EMOJI = {
    "clara": "🟢",
    "moderada": "🟡",
    "dificil": "🔴"
}


class AnnotationApp:
    """App de anotação manual de notícias"""

    def __init__(self):
        # Detectar ambiente (local ou GCP)
        self.use_gcs = os.getenv('USE_GCS', 'false').lower() == 'true'
        self.bucket_name = os.getenv('GCS_BUCKET', 'dgb-streamlit-data')

        # Inicializar data loader
        self.data_loader = DataLoader(use_gcs=self.use_gcs, bucket_name=self.bucket_name)

        # Nomes dos arquivos
        self.dataset_filename = os.getenv('DATASET_FILE', 'test_dataset.csv')
        self.themes_filename = os.getenv('THEMES_FILE', 'themes_tree_enriched_full.yaml')
        self.agencies_filename = 'agencies.yaml'

        # Inicializar agency loader
        data_dir = Path(__file__).parent.parent / 'data'
        agencies_file = data_dir / self.agencies_filename
        self.agency_loader = AgencyLoader(agencies_file) if agencies_file.exists() else None

    def load_data(self):
        """Carrega dataset e árvore temática (sem cache para suportar trabalho em paralelo)"""
        try:
            df = self.data_loader.load_csv(self.dataset_filename)
            themes_tree = self.data_loader.load_yaml(self.themes_filename)
            return df, themes_tree
        except FileNotFoundError as e:
            st.error(f"❌ Erro ao carregar dados: {e}")
            st.info("💡 Certifique-se de que os arquivos estão no local correto:")
            st.code(f"- {self.dataset_filename}\n- {self.themes_filename}")
            st.stop()

    def save_annotation(self, index, l1_code, l2_code, l3_code, confidence, observations, annotator_name):
        """
        Salva anotação recarregando dataset antes (para evitar conflitos em trabalho paralelo)

        Args:
            index: Índice da notícia no dataset
            l1_code, l2_code, l3_code: Códigos de classificação
            confidence: Nível de confiança
            observations: Observações
            annotator_name: Nome do anotador
        """
        # 1. Recarregar dataset para pegar mudanças de outros usuários
        df = self.data_loader.load_csv(self.dataset_filename)

        # 2. Atualizar apenas a linha específica
        df.loc[index, 'L1_anotado'] = l1_code
        df.loc[index, 'L2_anotado'] = l2_code
        df.loc[index, 'L3_anotado'] = l3_code
        df.loc[index, 'confianca'] = confidence
        df.loc[index, 'observacoes'] = observations
        df.loc[index, 'anotador'] = annotator_name
        df.loc[index, 'data_anotacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 3. Salvar dataset atualizado
        self.data_loader.save_csv(df, self.dataset_filename)

    def get_agency_name(self, sigla: str) -> str:
        """Obtém nome completo da agência"""
        if self.agency_loader:
            return self.agency_loader.get_agency_name(sigla)
        return sigla

    def get_theme_label(self, code: str, themes: dict) -> str:
        """
        Obtém o label de um tema a partir do código.

        Args:
            code: Código do tema (ex: "01", "01.01", "01.01.01")
            themes: Dicionário com hierarquia de temas

        Returns:
            Label do tema ou código se não encontrado
        """
        if not code or not themes:
            return code

        # Determinar nível
        parts = str(code).split('.')
        level = len(parts)

        if level == 1:
            # L1
            return themes['L1'].get(code, code)
        elif level == 2:
            # L2
            parent = parts[0]
            return themes['L2'].get(parent, {}).get(code, code)
        elif level == 3:
            # L3
            parent = '.'.join(parts[:2])
            return themes['L3'].get(parent, {}).get(code, code)

        return code

    def render_home_page(self):
        """Renderiza página inicial com instruções"""
        st.title("📋 Anotação Manual de Notícias GovBR")
        st.markdown("### Fase 4.3 - Validação da Taxonomia Temática")

        st.markdown("---")

        # Instruções
        st.markdown("""
        ## 🎯 Objetivo

        Esta ferramenta permite a **anotação manual de notícias governamentais brasileiras**
        com classificação temática hierárquica em 3 níveis:

        - **L1 (Tema)**: Área temática principal (ex: "Economia e Finanças")
        - **L2 (Subtema)**: Subcategoria do tema (ex: "Política Econômica")
        - **L3 (Categoria)**: Classificação específica (ex: "Política Fiscal")

        ## 📝 Como Anotar

        1. **Leia** o título, resumo e conteúdo da notícia
        2. **Identifique** o tema principal (L1)
        3. **Selecione** o subtema (L2) e categoria (L3) mais específicos
        4. **Avalie** seu nível de confiança na classificação
        5. **Documente** observações para casos ambíguos ou dúvidas
        6. **Salve** a anotação e passe para a próxima notícia

        ## ✅ Dicas de Qualidade

        - Sempre escolha a **categoria mais específica** possível
        - Para notícias **multi-temáticas**, priorize o tema **dominante**
        - Use **"Confiança Baixa"** quando houver **ambiguidade**
        - Documente **dúvidas** no campo de observações
        - Consulte a **classificação original** (ground truth) se disponível

        ## 🚀 Filtros Disponíveis

        - **Status**: Todas / Pendentes / Anotadas
        - **Complexidade**:
          - 🟢 Clara: Tema óbvio
          - 🟡 Moderada: Requer análise
          - 🔴 Difícil: Ambígua ou multi-temática

        ---
        """)

        # Nome do anotador
        st.markdown("## 👤 Identificação")

        # Carregar nome do cookie (session_state)
        if 'annotator_name' not in st.session_state:
            st.session_state.annotator_name = ""

        annotator_name = st.text_input(
            "**Seu Nome**",
            value=st.session_state.annotator_name,
            placeholder="Digite seu nome completo",
            help="Seu nome será salvo junto com cada anotação que você fizer"
        )

        # Atualizar session state
        if annotator_name:
            st.session_state.annotator_name = annotator_name

        # Botão para iniciar
        if st.button("🚀 Iniciar Anotação", type="primary", use_container_width=True):
            if not annotator_name:
                st.error("⚠️ Por favor, informe seu nome antes de iniciar")
            else:
                st.session_state.show_home = False
                st.rerun()

    def render_sidebar(self, df, current_pos=None, total_filtered=None):
        """Renderiza sidebar com estatísticas e filtros"""
        with st.sidebar:
            # Nome do anotador (topo)
            st.markdown(f"### 👤 {st.session_state.annotator_name}")

            if st.button("🏠 Voltar para Home"):
                st.session_state.show_home = True
                st.rerun()

            st.markdown("---")

            # Contador de notícia atual
            if current_pos is not None and total_filtered is not None:
                st.info(f"📄 **Notícia {current_pos + 1} de {total_filtered}**")
                st.markdown("---")

            st.header("📊 Progresso")

            total = len(df)
            anotadas = df['L1_anotado'].notna().sum()
            pendentes = total - anotadas
            progresso = (anotadas / total) * 100 if total > 0 else 0

            st.metric("Total", total)
            st.metric("Anotadas", f"{anotadas} ({progresso:.1f}%)")
            st.metric("Pendentes", pendentes)

            st.progress(progresso / 100)

            st.markdown("---")

            # Filtros
            st.subheader("🔍 Filtros")

            filtro_status = st.selectbox(
                "Status",
                ["Todas", "Pendentes", "Anotadas"],
                help="Filtrar notícias por status de anotação"
            )

            filtro_complexidade = st.selectbox(
                "Complexidade",
                ["Todas", "clara", "moderada", "dificil"],
                format_func=lambda x: f"{COMPLEXITY_EMOJI.get(x, '')} {x}".strip() if x != "Todas" else x,
                help="Filtrar por complexidade estimada da classificação"
            )

            return filtro_status, filtro_complexidade

    def apply_filters(self, df, filtro_status, filtro_complexidade):
        """Aplica filtros ao dataframe"""
        df_filtrado = df.copy()

        if filtro_status == "Pendentes":
            df_filtrado = df_filtrado[df_filtrado['L1_anotado'].isna()]
        elif filtro_status == "Anotadas":
            df_filtrado = df_filtrado[df_filtrado['L1_anotado'].notna()]

        if filtro_complexidade != "Todas":
            df_filtrado = df_filtrado[df_filtrado['complexidade_estimada'] == filtro_complexidade]

        return df_filtrado

    def render_news_content(self, row):
        """Renderiza conteúdo da notícia"""
        # CSS customizado para melhor hierarquia visual
        st.markdown("""
        <style>
        .sticky-title {
            position: sticky;
            top: 0;
            z-index: 999;
            background-color: var(--background-color);
            padding: 1rem 0;
            border-bottom: 2px solid var(--primary-color);
            margin-bottom: 1rem;
        }
        .content-section {
            background-color: var(--secondary-background-color);
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 2rem;
            border-left: 4px solid var(--primary-color);
        }
        /* Estilizar containers com borda */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
            padding: 1.5rem !important;
            border-radius: 0.75rem !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
            margin-bottom: 1rem !important;
        }

        /* Container do resumo (azul) */
        .content-section div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: rgba(33, 195, 230, 0.05) !important;
            border: 2px solid #21c3e6 !important;
            border-left: 4px solid #21c3e6 !important;
        }

        /* Container do formulário de classificação (vermelho) */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"]:last-of-type {
            background-color: #f0f2f6 !important;
            padding: 2rem !important;
            border: 3px solid #ff4b4b !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15) !important;
            margin-top: 2rem !important;
        }
        .form-section-title {
            font-size: 1.5rem !important;
            font-weight: bold !important;
            color: #ff4b4b !important;
            margin-bottom: 1rem !important;
            padding-bottom: 0.5rem !important;
            border-bottom: 2px solid #ff4b4b !important;
        }
        .resumo-destaque {
            font-size: 1.1rem;
            line-height: 1.6;
            padding: 1rem;
            background-color: rgba(33, 195, 230, 0.1);
            border-radius: 0.5rem;
            border-left: 4px solid #21c3e6;
        }
        </style>
        """, unsafe_allow_html=True)

        # Container para a seção de conteúdo
        st.markdown('<div class="content-section">', unsafe_allow_html=True)

        # Título da notícia (grande e destacado)
        st.markdown(f'<div class="sticky-title"><h2>📰 {row["titulo"]}</h2></div>', unsafe_allow_html=True)

        # Resumo (se existir) - com mais destaque usando container
        if pd.notna(row['resumo']) and row['resumo']:
            resumo_container = st.container(border=True)
            with resumo_container:
                st.markdown("**📝 Resumo**")
                st.markdown(f'<div style="font-size: 1.1rem; line-height: 1.6;">{row["resumo"]}</div>', unsafe_allow_html=True)
            st.markdown("")  # Espaçamento

        # Conteúdo início (expansível e compacto)
        if pd.notna(row['conteudo_inicio']) and row['conteudo_inicio']:
            with st.expander("📄 Conteúdo (500 caracteres)", expanded=False):
                st.text(row['conteudo_inicio'])

        st.markdown("")  # Espaçamento

        # Formatar data para dd/mm/yyyy
        from datetime import datetime
        try:
            if pd.notna(row['data_publicacao']):
                # Tentar parsear a data
                date_str = str(row['data_publicacao'])
                if 'T' in date_str:  # ISO format
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                else:
                    dt = datetime.strptime(date_str[:10], '%Y-%m-%d')
                formatted_date = dt.strftime('%d/%m/%Y')
            else:
                formatted_date = "N/A"
        except:
            formatted_date = str(row['data_publicacao'])

        agency_name = self.get_agency_name(row['orgao'])
        complexity = row['complexidade_estimada']
        emoji = COMPLEXITY_EMOJI.get(complexity, "")

        # Dicionário de explicações para complexidade
        complexity_tooltips = {
            "clara": "Notícia objetiva com tema evidente e fácil de classificar",
            "moderada": "Notícia com tema identificável mas que pode ter alguma ambiguidade",
            "difícil": "Notícia ambígua, multitemática ou com tema pouco claro"
        }
        tooltip = complexity_tooltips.get(complexity, "Complexidade da classificação temática")

        # Metadados compactos em uma linha (pequeno e discreto)
        # Complexidade com tooltip usando HTML
        complexity_html = f'<span title="{tooltip}" style="cursor: help; border-bottom: 1px dotted #666;">{emoji} {complexity}</span>'

        metadata_parts = [
            f"**Órgão:** {agency_name}",
            f"**Data:** {formatted_date}",
            f"**Complexidade:** {complexity_html}"
        ]

        if row['url']:
            metadata_parts.append(f"[🔗 Link]({row['url']})")

        st.markdown(f'<small>{" | ".join(metadata_parts)}</small>', unsafe_allow_html=True)

        # Fechar container de conteúdo
        st.markdown('</div>', unsafe_allow_html=True)

    def render_hierarchical_selection(self, row, themes):
        """
        Renderiza seleção hierárquica L1 → L2 → L3 FORA do form.

        IMPORTANTE: Não pode estar dentro de st.form() para permitir reatividade.
        """
        # Nota: A abertura da div form-section agora é feita externamente

        # Inicializar session state para as seleções
        if 'selected_l1' not in st.session_state:
            st.session_state.selected_l1 = ""
        if 'selected_l2' not in st.session_state:
            st.session_state.selected_l2 = ""
        if 'selected_l3' not in st.session_state:
            st.session_state.selected_l3 = ""

        # Verificar se temos valores anotados para esta notícia
        if pd.notna(row['L1_anotado']) and str(row['L1_anotado']):
            current_l1 = str(row['L1_anotado'])
        else:
            current_l1 = st.session_state.selected_l1

        if pd.notna(row['L2_anotado']) and str(row['L2_anotado']):
            current_l2 = str(row['L2_anotado'])
        else:
            current_l2 = st.session_state.selected_l2

        if pd.notna(row['L3_anotado']) and str(row['L3_anotado']):
            current_l3 = str(row['L3_anotado'])
        else:
            current_l3 = st.session_state.selected_l3

        # L1 - Tema
        l1_options = [""] + [f"{code} - {label}" for code, label in sorted(themes['L1'].items())]

        l1_current_formatted = ""
        if current_l1:
            matches = [x for x in l1_options if x.startswith(current_l1)]
            if matches:
                l1_current_formatted = matches[0]

        l1_index = l1_options.index(l1_current_formatted) if l1_current_formatted in l1_options else 0

        l1_selected = st.selectbox(
            "**Tema (L1)**",
            l1_options,
            index=l1_index,
            key="l1_selector",
            help="Selecione o tema principal da notícia"
        )

        # Atualizar session state
        st.session_state.selected_l1 = l1_selected.split(' - ')[0] if l1_selected else ""

        # Inicializar variáveis de retorno
        l2_selected = None
        l3_selected = None

        # L2 - Subtema (só aparece se L1 selecionado)
        if l1_selected:
            l1_code = l1_selected.split(' - ')[0]
            l2_options = [""] + [f"{code} - {label}" for code, label in sorted(themes['L2'].get(l1_code, {}).items())]

            l2_current_formatted = ""
            if current_l2 and current_l2.startswith(l1_code):
                matches = [x for x in l2_options if x.startswith(current_l2)]
                if matches:
                    l2_current_formatted = matches[0]

            l2_index = l2_options.index(l2_current_formatted) if l2_current_formatted in l2_options else 0

            l2_selected = st.selectbox(
                "**Subtema (L2)**",
                l2_options,
                index=l2_index,
                key="l2_selector",
                help="Selecione o subtema mais específico"
            )

            # Atualizar session state
            st.session_state.selected_l2 = l2_selected.split(' - ')[0] if l2_selected else ""

            # L3 - Categoria (só aparece se L2 selecionado)
            if l2_selected:
                l2_code = l2_selected.split(' - ')[0]
                l3_options = [""] + [f"{code} - {label}" for code, label in sorted(themes['L3'].get(l2_code, {}).items())]

                l3_current_formatted = ""
                if current_l3 and current_l3.startswith(l2_code):
                    matches = [x for x in l3_options if x.startswith(current_l3)]
                    if matches:
                        l3_current_formatted = matches[0]

                l3_index = l3_options.index(l3_current_formatted) if l3_current_formatted in l3_options else 0

                l3_selected = st.selectbox(
                    "**Categoria (L3)**",
                    l3_options,
                    index=l3_index,
                    key="l3_selector",
                    help="Selecione a categoria mais específica"
                )

                # Atualizar session state
                st.session_state.selected_l3 = l3_selected.split(' - ')[0] if l3_selected else ""

        return l1_selected, l2_selected, l3_selected

    def render_annotation_form(self, row, l1_selected):
        """
        Renderiza apenas os campos finais do formulário (confiança, observações, botões).

        IMPORTANTE: A seleção L1/L2/L3 deve estar FORA do form.
        """
        st.markdown("")
        st.markdown("**📊 Avaliação da Classificação**")

        with st.form(key="annotation_form"):
            # Confiança
            conf_value = "media"
            if pd.notna(row['confianca']) and row['confianca'] in ["baixa", "media", "alta"]:
                conf_value = row['confianca']

            confianca = st.select_slider(
                "**Confiança na Classificação**",
                options=["baixa", "media", "alta"],
                value=conf_value,
                help="Quão confiante você está nesta classificação?"
            )

            # Observações
            obs_value = ""
            if pd.notna(row['observacoes']):
                obs_value = str(row['observacoes'])

            observacoes = st.text_area(
                "**Observações** (opcional)",
                value=obs_value,
                placeholder="Casos ambíguos, dúvidas, comentários...",
                help="Documente qualquer observação relevante sobre a classificação"
            )

            # Botões
            col_btn1, col_btn2 = st.columns(2)

            with col_btn1:
                # Desabilitar botão se L1 não estiver selecionado
                # Verificar se l1_selected é uma string não vazia (não apenas espaços)
                is_disabled = not l1_selected or str(l1_selected).strip() == ""
                submit = st.form_submit_button(
                    "💾 Salvar Anotação",
                    type="primary",
                    use_container_width=True,
                    disabled=is_disabled
                )

            with col_btn2:
                skip = st.form_submit_button("⏭️ Pular", use_container_width=True)

        # Nota: O fechamento da div form-section agora é feito externamente

        return submit, skip, confianca, observacoes

    def render_ground_truth(self, row, themes):
        """Renderiza classificação original (ground truth) com código E label"""
        if pd.notna(row['L1_original']) and row['L1_original']:
            with st.expander("🔍 Ver Classificação Original (Ground Truth)"):
                l1_code = str(row['L1_original'])
                l1_label = self.get_theme_label(l1_code, themes)
                st.markdown(f"**L1:** `{l1_code}` - {l1_label}")

                if pd.notna(row['L2_original']):
                    l2_code = str(row['L2_original'])
                    l2_label = self.get_theme_label(l2_code, themes)
                    st.markdown(f"**L2:** `{l2_code}` - {l2_label}")

                if pd.notna(row['L3_original']):
                    l3_code = str(row['L3_original'])
                    l3_label = self.get_theme_label(l3_code, themes)
                    st.markdown(f"**L3:** `{l3_code}` - {l3_label}")

    def run(self):
        """Executa aplicação principal"""
        # Verificar query params para modo de teste direto
        query_params = st.query_params
        direct_mode = query_params.get("direct", "false").lower() == "true"

        # Inicializar session state
        if 'show_home' not in st.session_state:
            st.session_state.show_home = not direct_mode  # Se direct_mode, não mostra home

        # Modo direto para testes: pula home e define nome padrão
        if direct_mode and 'annotator_name' not in st.session_state:
            st.session_state.annotator_name = "Test User"
            st.session_state.show_home = False

        # Mostrar home se necessário
        if st.session_state.show_home:
            self.render_home_page()
            return

        # Aplicação principal (sem título grande para economizar espaço)

        # Carregar dados
        df, themes_tree = self.load_data()
        themes = get_theme_hierarchy(themes_tree)

        # Primeiro passo: aplicar filtros para obter índices e posição
        # Fazer uma primeira passagem sem renderizar sidebar
        df_filtrado_temp = df.copy()
        if 'filter_status' in st.session_state and st.session_state.filter_status != "Todas":
            if st.session_state.filter_status == "Pendentes":
                df_filtrado_temp = df_filtrado_temp[df_filtrado_temp['L1_anotado'].isna()]
            elif st.session_state.filter_status == "Anotadas":
                df_filtrado_temp = df_filtrado_temp[df_filtrado_temp['L1_anotado'].notna()]

        if 'filter_complexity' in st.session_state and st.session_state.filter_complexity != "Todas":
            df_filtrado_temp = df_filtrado_temp[df_filtrado_temp['complexidade_estimada'] == st.session_state.filter_complexity]

        # Seletor de notícia - escolha aleatória ao iniciar para evitar conflitos entre anotadores
        indices = df_filtrado_temp.index.tolist()
        if 'current_index' not in st.session_state:
            if len(indices) > 0:
                # Escolher aleatoriamente entre as notícias pendentes
                st.session_state.current_index = random.choice(indices)
            else:
                st.session_state.current_index = df.index[0]

        # Garantir que o índice atual está na lista filtrada
        if st.session_state.current_index not in indices and len(indices) > 0:
            st.session_state.current_index = indices[0]

        current_pos = indices.index(st.session_state.current_index) if st.session_state.current_index in indices else 0

        # Agora renderizar sidebar COM o contador correto
        filtro_status, filtro_complexidade = self.render_sidebar(df, current_pos, len(indices))

        # Atualizar session state se filtros mudaram
        st.session_state.filter_status = filtro_status
        st.session_state.filter_complexity = filtro_complexidade

        # Aplicar filtros finais (pode ter mudado)
        df_filtrado = self.apply_filters(df, filtro_status, filtro_complexidade)

        # Verificar se há notícias para anotar
        if len(df_filtrado) == 0:
            st.info("✅ Todas as notícias foram anotadas!")
            return

        # Atualizar índices se mudou
        indices = df_filtrado.index.tolist()
        if st.session_state.current_index not in indices:
            st.session_state.current_index = indices[0]

        current_pos = indices.index(st.session_state.current_index)

        # Navegação compacta (apenas botões, sem contador no meio)
        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("⬅️ Anterior", use_container_width=True):
                if current_pos > 0:
                    st.session_state.current_index = indices[current_pos - 1]
                    # Limpar seleções ao mudar de notícia
                    st.session_state.selected_l1 = ""
                    st.session_state.selected_l2 = ""
                    st.session_state.selected_l3 = ""
                    st.rerun()

        with col2:
            if st.button("Próxima ➡️", use_container_width=True):
                if current_pos < len(indices) - 1:
                    st.session_state.current_index = indices[current_pos + 1]
                    # Limpar seleções ao mudar de notícia
                    st.session_state.selected_l1 = ""
                    st.session_state.selected_l2 = ""
                    st.session_state.selected_l3 = ""
                    st.rerun()

        st.markdown("---")

        # Exibir notícia atual
        row = df.loc[st.session_state.current_index]

        # Layout em 2 colunas: Notícia | Formulário
        col_news, col_form = st.columns([1.2, 1])

        # Coluna 1: Notícia
        with col_news:
            # Renderizar conteúdo da notícia (a âncora está dentro do método)
            self.render_news_content(row)

        # Coluna 2: Formulário de Classificação
        with col_form:
            # === INÍCIO da caixa de Classificação Temática ===
            # Usar container do Streamlit
            classification_container = st.container(border=True)

            with classification_container:
                # Título da seção dentro da caixa
                st.markdown('<div class="form-section-title">🏷️ Classificação Temática</div>', unsafe_allow_html=True)
                st.markdown("Selecione a classificação hierárquica da notícia:")
                st.markdown("")

                # Renderizar seleção hierárquica FORA do form
                l1_selected, l2_selected, l3_selected = self.render_hierarchical_selection(row, themes)

                # Renderizar formulário (apenas campos finais) - passar l1_selected para desabilitar botão
                submit, skip, confianca, observacoes = self.render_annotation_form(row, l1_selected)

            # Mostrar ground truth dentro da coluna de classificação
            self.render_ground_truth(row, themes)

        if submit:
            if not l1_selected:
                st.error("⚠️ Selecione pelo menos o Tema (L1)")
            else:
                # Extrair códigos (remover labels)
                l1_code = l1_selected.split(' - ')[0]
                l2_code = l2_selected.split(' - ')[0] if l2_selected else ''
                l3_code = l3_selected.split(' - ')[0] if l3_selected else ''

                # Animação de salvamento
                with st.spinner('💾 Salvando anotação...'):
                    import time
                    time.sleep(0.5)  # Breve pausa para mostrar o spinner
                    # Salvar usando novo método que recarrega antes de escrever
                    self.save_annotation(
                        index=st.session_state.current_index,
                        l1_code=l1_code,
                        l2_code=l2_code,
                        l3_code=l3_code,
                        confidence=confianca,
                        observations=observacoes,
                        annotator_name=st.session_state.annotator_name
                    )

                # Progress bar de confirmação
                progress_bar = st.progress(0)
                for percent_complete in range(100):
                    time.sleep(0.005)  # 0.5 segundos total
                    progress_bar.progress(percent_complete + 1)

                st.success("✅ Anotação salva com sucesso!")
                time.sleep(0.5)  # Mostrar mensagem de sucesso brevemente

                # Ir para próxima
                current_pos = indices.index(st.session_state.current_index)
                if current_pos < len(indices) - 1:
                    st.session_state.current_index = indices[current_pos + 1]

                # Limpar seleções
                st.session_state.selected_l1 = ""
                st.session_state.selected_l2 = ""
                st.session_state.selected_l3 = ""

                st.rerun()

        if skip:
            # Pular para uma notícia aleatória (evita conflitos e distribui trabalho)
            if len(indices) > 1:
                # Escolher aleatoriamente entre as outras notícias (exceto a atual)
                other_indices = [idx for idx in indices if idx != st.session_state.current_index]
                if other_indices:
                    st.session_state.current_index = random.choice(other_indices)
                else:
                    # Se só tem uma notícia, manter a atual
                    st.session_state.current_index = indices[0]

                # Limpar seleções
                st.session_state.selected_l1 = ""
                st.session_state.selected_l2 = ""
                st.session_state.selected_l3 = ""

                st.rerun()


def main():
    """Função principal"""
    app = AnnotationApp()
    app.run()


if __name__ == "__main__":
    main()
