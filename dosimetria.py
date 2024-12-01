import streamlit as st
import pdfplumber
import pandas as pd
import re
import os
import openpyxl
import csv
import time
from tqdm import tqdm


def extract_pdf_data(pdf_path):
    """
    Extrai informações-chave de um relatório de dosimetria em PDF.
    """
    extracted_data = {
        'razao_social': None,
        'nome_avaliado': None,
        'cargo': None,
        'incremento': None,
        'tipo_dose': None,
        'dose': None,
        'dose_projetada': None,
        'nen': None
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            text = page.extract_text()

            # Razão Social
            razao_social_match = re.search(r'Razão Social:\s*([^\n]+)', text)
            if razao_social_match:
                extracted_data['razao_social'] = razao_social_match.group(1).strip()

            # Nome do Avaliado
            nome_avaliado_match = re.search(r'Nome do Avaliado:\s*([^\n]+)', text)
            if nome_avaliado_match:
                extracted_data['nome_avaliado'] = nome_avaliado_match.group(1).strip()

            # Cargo
            cargo_match = re.search(r'Cargo:\s*([^\n]+)', text)
            if cargo_match:
                extracted_data['cargo'] = cargo_match.group(1).strip()

            # Incremento de Duplicação de Dose
            incremento_match = re.search(r'Incremento de Duplicação Dose:\s*(\d+)', text)
            if incremento_match:
                extracted_data['incremento'] = incremento_match.group(1).strip()

            # Utilização da Dose
            utilizacao_dose_match = re.search(r'Utilização da DOSE ou DOSE Projetada:\s*([^\n]+)', text)
            if utilizacao_dose_match:
                extracted_data['tipo_dose'] = utilizacao_dose_match.group(1).strip()

            # Dose
            dose_match = re.search(r'DOSE:\s*(\d+(?:,\d+)?%)', text)
            if dose_match:
                extracted_data['dose'] = dose_match.group(1).strip()

            # Dose Projetada
            dose_projetada_match = re.search(r'DOSE Projetada:\s*(\d+(?:,\d+)?%)', text)
            if dose_projetada_match:
                extracted_data['dose_projetada'] = dose_projetada_match.group(1).strip()

            # Nível de Exposição Normalizada (NEN)
            nen_match = re.search(r'Nível de Exposição Normalizada \(NEN\):\s*(\d+(?:,\d+)?\s*dB\(A\))', text)
            if nen_match:
                extracted_data['nen'] = nen_match.group(1).strip()

    except Exception as e:
        raise Exception(f"Erro ao processar o arquivo {pdf_path}: {e}")

    return extracted_data


def process_directory(directory):
    """
    Processa todos os PDFs de um diretório e salva os resultados em arquivos Excel e CSV.
    """
    pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
    if not pdf_files:
        raise Exception("Nenhum arquivo PDF encontrado no diretório.")

    excel_path = os.path.join(directory, "relatorios_dosimetria.xlsx")
    csv_path = os.path.join(directory, "relatorios_dosimetria.csv")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Dados Extraídos"
    headers = ['RAZÃO SOCIAL', 'NOME AVALIADO', 'CARGO', 'INCREMENTO', 
               'USO DOSE', 'DOSE', 'DOSE PROJETADA', 'NEN', 'NOME DO ARQUIVO', 'STATUS']
    ws.append(headers)

    with open(csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(headers)

        start_time = time.time()  # Iniciar o cronômetro de tempo
        total_files = len(pdf_files)

        # Exibir o progresso do processamento com um "spinner"
        with st.spinner(f"Processando {total_files} arquivos..."):
            for pdf_file in tqdm(pdf_files, desc="Processando PDFs", position=0, leave=True):
                full_path = os.path.join(directory, pdf_file)
                try:
                    data = extract_pdf_data(full_path)
                    
                    row_data = [
                        data['razao_social'] or 'N/A', 
                        data['nome_avaliado'] or 'N/A',
                        data['cargo'] or 'N/A', 
                        data['incremento'] or 'N/A', 
                        data['tipo_dose'] or 'N/A',
                        data['dose'] or 'N/A',
                        data['dose_projetada'] or 'N/A', 
                        data['nen'] or 'N/A', 
                        pdf_file, 
                        "Concluído"
                    ]
                    
                    ws.append(row_data)
                    csv_writer.writerow(row_data)

                except Exception as e:
                    ws.append(['N/A'] * 7 + [pdf_file, f"Erro: {e}"])
                    csv_writer.writerow(['N/A'] * 7 + [pdf_file, f"Erro: {e}"])

        # Calcular o tempo total
        end_time = time.time()
        total_time = end_time - start_time
        st.success(f"Processamento concluído! **Tempo total:** {
                   total_time:.2f} segundos. \n**Arquivos Processados**: {total_files}")

        # Mostrar resumo de arquivos processados
        st.write(f"**Arquivos Processados**: {total_files}")
        st.write(f"**Tempo de Processamento**: {total_time:.2f} segundos")

    wb.save(excel_path)


def show_dosimetria_page():
    st.header("🔊Relatórios de Dosimetrias")

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
                temp_path = "temp_dos.pdf"
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

        uploaded_files = st.file_uploader(
            "Faça upload de múltiplos arquivos PDF",
            accept_multiple_files=True,
            type=['pdf']
        )

        use_directory = st.checkbox("Selecionar diretório no computador")

        if use_directory:
            directory = st.text_input(
                "Informe o caminho do diretório contendo os PDFs:",
                help="Digite o caminho completo para a pasta com PDFs"
            )

        if st.button("🚀 Iniciar extração dos dados"):
            with st.spinner("Processando arquivos..."):
                try:
                    if uploaded_files:
                        # Process uploaded files
                        all_results = []
                        for uploaded_file in uploaded_files:
                            temp_path = f"temp_{uploaded_file.name}"
                            with open(temp_path, "wb") as f:
                                f.write(uploaded_file.read())

                            extracted_data = extract_pdf_data(temp_path)
                            if extracted_data["dados_tabela"] is not None:
                                extracted_data["dados_tabela"]["Arquivo_Origem"] = uploaded_file.name
                                all_results.append(
                                    extracted_data["dados_tabela"])
                            os.remove(temp_path)

                        # Consolidate results
                        if all_results:
                            consolidated_df = pd.concat(
                                all_results, ignore_index=True)

                            st.download_button(
                                label="📥 Baixar como Excel",
                                data=consolidated_df.to_excel(index=False),
                                file_name="dados_processados.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

                            st.success(
                                f"✅ {len(all_results)} arquivos processados!")
                        else:
                            st.warning(
                                "Nenhuma tabela encontrada nos arquivos")

                    elif use_directory and directory:
                        # Existing directory processing logic
                        process_directory(directory)
                        st.success(
                            f"✅Arquivos processados no diretório: {directory}")

                    else:
                        st.warning(
                            "Selecione arquivos ou um diretório para processar")

                except Exception as e:
                    st.error(f"❌Erro durante o processamento: {e}")
