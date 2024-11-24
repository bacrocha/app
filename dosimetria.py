import streamlit as st

def show_dosimetria_page():
    st.header("🔊Relatórios de Dosimetrias")
    st.warning("⚠️ Módulo em desenvolvimento")
        
    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown("""
            ### Funcionalidades Previstas:
            - Extração automática de dados de dosimetrias
            - Exportação de resultados para Excel e CSV
                
            **Previsão de lançamento:** Em breve
        """)

# Rodapé
st.markdown("---")            