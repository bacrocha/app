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
    Extrai informações-chave de um relatório de análise química em PDF.
    """
    extracted_data = {
        'empresa_avaliada': None,
        'amostrador': None,
        'metodologia': None,
        'dados_tabela': None,
        'numero_relatorio': None
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            text = page.extract_text()

            # Extração de campos específicos
            extracted_data['empresa_avaliada'] = re.search(
                r'Empresa avaliada:\s*([^\n|]+)', text).group(1).strip()

            extracted_data['amostrador'] = re.search(
                r'Nº do Amostrador:\s*([\w-]+)', text).group(1).strip()

            metodologia_match = re.search(
                r'3 - MÉTODO\s*\(s\)\s*\n(.*?)(?=\n4 -|$)', text)
            if metodologia_match:
                extracted_data['metodologia'] = metodologia_match.group(
                    1).strip()

            extracted_data['numero_relatorio'] = re.search(
                r'Relatório de Análise - Nº\s*(\d+-\d+)', text).group(1).strip()

            # Extração da tabela
            table = page.extract_tables()
            if table and len(table[0]) > 1:
                headers = ['Agente Químico', 'Unidade', 'Resultado',
                           'MP 8h', 'Teto', 'TWA', 'STEL', 'Ceiling', 'LD']
                data_rows = [
                    [str(cell).strip()
                     if cell else 'N/A' for cell in row[:len(headers)]]
                    for row in table[0]
                    if any(x in ' '.join(map(str, row)) for x in ['ppm', 'mg/m³'])
                ]
                if data_rows:
                    extracted_data['dados_tabela'] = pd.DataFrame(
                        data_rows, columns=headers)

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

    excel_path = os.path.join(directory, "relatorios_quimica.xlsx")
    csv_path = os.path.join(directory, "relatorios_quimica.csv")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Dados Extraídos"
    headers = ['EMPRESA AVALIADA', 'AMOSTRADOR', 'METODOLOGIA', 'NÚMERO RELATÓRIO',
               'AGENTE QUÍMICO', 'UNIDADE', 'RESULTADO', 'MP 8h', 'TETO',
               'TWA', 'STEL', 'CEILING', 'NOME DO ARQUIVO', 'STATUS']
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
                    if data['dados_tabela'] is not None:
                        for _, row in data['dados_tabela'].iterrows():
                            row_data = [
                                data['empresa_avaliada'], data['amostrador'],
                                data['metodologia'], data['numero_relatorio'],
                                row.get('Agente Químico', 'N/A'),
                                row.get('Unidade', 'N/A'),
                                row.get('Resultado', 'N/A'),
                                row.get('MP 8h', 'N/A'), row.get('Teto', 'N/A'),
                                row.get('TWA', 'N/A'), row.get('STEL', 'N/A'),
                                row.get('Ceiling', 'N/A'), pdf_file, "Concluído"
                            ]
                            ws.append(row_data)
                            csv_writer.writerow(row_data)
                except Exception as e:
                    ws.append(['N/A'] * 12 + [pdf_file, f"Erro: {e}"])
                    csv_writer.writerow(
                        ['N/A'] * 12 + [pdf_file, f"Erro: {e}"])

        # Calcular o tempo total
        end_time = time.time()
        total_time = end_time - start_time
        st.success(f"Processamento concluído! **Tempo total:** {
                   total_time:.2f} segundos. \n**Arquivos Processados**: {total_files}")

        # Mostrar resumo de arquivos processados
        st.write(f"**Arquivos Processados**: {total_files}")
        st.write(f"**Tempo de Processamento**: {total_time:.2f} segundos")

    wb.save(excel_path)


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
