import streamlit as st
import os
import pandas as pd
from quimica_extractor import extract_pdf_data, process_directory

def show_quimica_page():
    st.header("🧪Relatórios de Análises Químicas")

    tab1, tab2 = st.tabs(["📄 Arquivo Único", "📁 Processamento em Lote"])

    with tab1:
        st.markdown("### Extração de Dados - PDF Único")
        uploaded_file = st.file_uploader(
            "Faça o upload do arquivo PDF",
            type=["pdf"]
        )

        if uploaded_file:
            with st.spinner("Processando o arquivo..."):
                # Salvar arquivo temporário
                temp_path = "temp_quimica.pdf"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())

                try:
                    # Extrair dados do PDF
                    extracted_data = extract_pdf_data(temp_path)
                    st.success("Dados extraídos com sucesso!")

                    # Exibir dados extraídos
                    st.subheader("Tabela Extraída")
                    if extracted_data["dados_tabela"] is not None:
                        st.dataframe(extracted_data["dados_tabela"])
                    else:
                        st.warning("Nenhuma tabela encontrada no arquivo.")

                except Exception as e:
                    st.error(f"Erro ao processar o arquivo: {e}")

                finally:
                    # Remover arquivo temporário
                    os.remove(temp_path)

    with tab2:
        st.markdown("### Processamento em Lote")
        directory = st.text_input(
            "Informe o diretório contendo os arquivos PDF:",
            help="Certifique-se de que o caminho está correto."
        )

        if st.button("🚀 Iniciar extração dos dados"):
            if os.path.isdir(directory):
                with st.spinner("Processando todos os arquivos..."):
                    try:
                        process_directory(directory)
                        st.success(f"✅Arquivos processados com sucesso! Resultados salvos no diretório: {directory}")
                    except Exception as e:
                        st.error(f"❌Erro durante o processamento: {e}")
            else:
                st.error("❌O caminho informado não é válido.")
