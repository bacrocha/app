import streamlit as st
# Importar os estilos personalizados
from styles import apply_custom_styles

# Configuração inicial da página
st.set_page_config(
    page_title="Sistema de Extração de Dados PDF",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Aplicar estilos customizados
#apply_custom_styles()

# Título principal
st.title("📄 Automação de Extração de Dados de Relatórios de Exposição Ocupacional")
st.markdown("---")

# Menu lateral de navegação
with st.sidebar:
    st.markdown("### ⚙️ Menu Principal")
    main_menu = st.radio(
        "Navegação",
        [
            "🏠 Início",
            "📄 Tipo do Relatório",
            "ℹ️ Sobre"
        ]
    )

# Lógica de navegação
if main_menu == "🏠 Início":
    st.markdown(
        """
        ### 🛠 Funcionalidades
        - Extraia dados de PDFs de maneira prática.
        - Processe relatórios de análises químicas, dosimetria e microbiologia.
        - Exporte resultados em Excel ou CSV.

        > **Dica**: Use a barra lateral para navegar entre as opções.
        """
    )

elif main_menu == "📄 Tipo do Relatório":
    # Submenu para "Tipo do Relatório"
    st.markdown("### 📂 Extração de Dados")
    report_type = st.selectbox(
        "Selecione o tipo de relatório",
        ["🧪Relatórios de Análises Químicas", "🔊Relatórios de Dosimetrias",
            "🧫Relatórios de Análises Microbiológicas"]
    )

    # Mostrar a página correspondente ao tipo de relatório
    if report_type == "🧪Relatórios de Análises Químicas":
        from quimica import show_quimica_page
        show_quimica_page()

    elif report_type == "🔊Relatórios de Dosimetrias":
        from dosimetria import show_dosimetria_page
        show_dosimetria_page()

    elif report_type == "🧫Relatórios de Análises Microbiológicas":
        from microbiologia import show_microbiologia_page
        show_microbiologia_page()

elif main_menu == "ℹ️ Sobre":
    st.markdown("### ℹ️ Sobre o Sistema")
    st.write("""
    Este sistema foi desenvolvido para facilitar a extração e organização de dados de relatórios em PDFs.
    É ideal para empresas que lidam com grandes volumes de informações laboratoriais.
    """)
    st.markdown("---")
    st.write("**Desenvolvedor:** Bárbara Rocha")
    st.write("📅 **Versão:** 1.0.0")

# Rodapé
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Desenvolvido por Bárbara Rocha | Versão 1.0.0
        \n© 2024 - Automação de Relatórios
    </div>
    """,
    unsafe_allow_html=True
)
