from reportlab.lib.pagesizes import letter
from ..DTO.relatorioDTO import ReportDTO
from io import StringIO
import os
import pandas as pd
from ..PDFGenerator import make_table, calculate_column_widths
from .Functions.Graphs.heatmap import generate_heatmap
from .Functions.Graphs.cake_plot import cake_plot
from .Functions.Graphs.bar_plot import bar_plot
from .Functions.Graphs.correlation_plot import generate_correlation_plot
from .Functions.Graphs.cake_plot_bigger_than_n import cake_plot_bigger_than_n
from .Functions.Statics.Stats import calculate_stats, filtered_by_word, mean_and_count_by, first_tenth
from .Functions.Graphs.multicolumns_bar_plot import multicolumns_bar_plot
from reportlab.lib.units import cm
from .Functions.Statics.data_process import convert_str_to_float, convert_str_to_datetime, convert_to_bool

import logging
from io import StringIO

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')


class GenericReport:
    def generate_bar_plot(self, data, column, report_dto, graph_sections):
        try:
            plot_path = bar_plot(data, column)
            section_key = f"Graph_Bar Plot for {column}"
            report_dto.add_section(section_key, plot_path)
            graph_sections.append(section_key)
            logging.info(f"Bar plot for {column} generated successfully. Path: {plot_path}")
        except Exception as e:
            logging.error(f"Failed to generate bar plot for {column}: {e}")
            report_dto.add_section(f"Bar Plot for {column}", "Graph generation failed")

    def create_report(self, data):
        report_dto = ReportDTO()
        graph_sections = []
        added_sections = []

        try:
            # Introductory Text
            columns = data.columns.tolist()
            col_string = ', '.join(columns)
            col_string_lines = self.split_text_into_lines(col_string, max_length=80)

            intro = f"The dataset contains {len(data)} rows and the following columns:\n" + '\n'.join(col_string_lines)
            report_dto.add_section("Introduction", intro)
            added_sections.append("Introduction")
            logging.info("Introduction section added.")
        except Exception as e:
            logging.error(f"Failed to add introduction section: {e}")

        try:
            # Capture Column Info before transformation
            buffer = StringIO()
            data.info(buf=buffer)
            col_info = buffer.getvalue()
            report_dto.add_section("Column Info", col_info)
            added_sections.append("Column Info")
            logging.info("Column Info section added.")
        except Exception as e:
            logging.error(f"Failed to add column info section: {e}")

        try:
            # Convert string columns to datetime where applicable
            data, datetime_converted_columns = convert_str_to_datetime(data)
            # Convert columns to bool where applicable
            data, bool_converted_columns = convert_to_bool(data)
            # Convert string columns to int where applicable
            data, int_converted_columns = convert_str_to_float(data)
        except Exception as e:
            logging.error(f"Failed to convert columns: {e}")

        try:
            # Capture Column Info after transformation
            buffer = StringIO()
            data.info(buf=buffer)
            col_info_transformed = buffer.getvalue()
            report_dto.add_section("Column Info Transformed", col_info_transformed)
            added_sections.append("Column Info Transformed")
            logging.info("Column Info Transformed section added.")
        except Exception as e:
            logging.error(f"Failed to add transformed column info section: {e}")

        try:
            # Add transformed columns to the report
            transformed_columns = (f"Converted to datetime: {', '.join(datetime_converted_columns)}\n"
                                   f"\nConverted to int: {', '.join(int_converted_columns)}\n"
                                   f"\nConverted to bool: {', '.join(bool_converted_columns)}\n")
            col_string_lines_transformed = self.split_text_into_lines(transformed_columns, max_length=80)
            report_dto.add_section("Transformed Columns", '\n'.join(col_string_lines_transformed))
            added_sections.append("Transformed Columns")
            logging.info("Transformed Columns section added.")
        except Exception as e:
            logging.error(f"Failed to add transformed columns section: {e}")

        try:
            # Separate columns by data type
            int_columns = data.select_dtypes(include='int').columns.tolist()
            float_columns = data.select_dtypes(include='float').columns.tolist()
            str_columns = data.select_dtypes(include='object').columns.tolist()
            bool_columns = data.select_dtypes(include='bool').columns.tolist()

            int_columns_lines = self.split_text_into_lines(', '.join(int_columns), max_length=80)
            float_columns_lines = self.split_text_into_lines(', '.join(float_columns), max_length=80)
            str_columns_lines = self.split_text_into_lines(', '.join(str_columns), max_length=80)

            report_dto.add_section("Integer Columns", '\n'.join(int_columns_lines))
            report_dto.add_section("Float Columns", '\n'.join(float_columns_lines))
            report_dto.add_section("String Columns", '\n'.join(str_columns_lines))
            report_dto.add_section("Boolean Columns", '\n'.join(bool_columns))
            added_sections.extend(["Integer Columns", "Float Columns", "String Columns", "Boolean Columns"])
            logging.info("Data type sections added.")
        except Exception as e:
            logging.error(f"Failed to add data type sections: {e}")

        try:
            # Create a table with the name of each column and the number of unique values
            unique_values_data = [[col, data[col].nunique()] for col in data.columns]
            unique_values_headers = ['Column Name', 'Unique Values Count']
            unique_values_column_widths = [440, 120]
            unique_values_table = make_table(unique_values_data, unique_values_headers, unique_values_column_widths)

            # Add the unique values table to the report
            report_dto.add_section("Table_Unique Values Count", unique_values_table)
            added_sections.append("Table_Unique Values Count")
            logging.info("Unique values count table added.")
        except Exception as e:
            logging.error(f"Failed to create unique values count table: {e}")

        try:
            # Identify Columns with All Different Values and Create "IDs" List
            ids_columns = []
            for column in data.columns:
                if data[column].nunique() >= 0.94 * len(data):
                    ids_columns.append(column)

            # Add "IDs" List to Report
            ids_list = ', '.join(ids_columns)
            report_dto.add_section("Possible IDs", ids_list)
            added_sections.append("Possible IDs")
        except Exception as e:
            logging.error(f"Failed to identify columns with all different values: {e}")

        try:
            # Combine int and float columns, convert to float for correlation plot
            numeric_columns = int_columns + float_columns

            # Exclude ids_columns from numeric_columns
            numeric_columns = [col for col in numeric_columns if col not in ids_columns]
        except Exception as e:
            logging.error(f"Failed to combine and exclude columns for correlation plot: {e}")

        try:
            # Generate Bar Plots for columns with less than 7 unique values
            for col in data.columns:
                unique_values = data[col].nunique()
                if unique_values <= 7:
                    self.generate_bar_plot(data, col, report_dto, graph_sections)
        except Exception as e:
            logging.error(f"Failed to generate bar plots for columns with less than 7 unique values: {e}")

        try:
            # Check if there is a column called "ESCOLARIDADE" and create education data table
            if 'ESCOLARIDADE' in str_columns:
                education_counts = data['ESCOLARIDADE'].value_counts()
                education_data = [[level, count] for level, count in education_counts.items()]
                education_headers = ['Nível de educação', 'Quantidade']
                education_column_widths = [500, 80]
                education_table = make_table(education_data, education_headers, education_column_widths)
                report_dto.add_section("Table_Education Levels", education_table)
                added_sections.append("Table_Education Levels")
                logging.info("Education levels table added.")
            else:
                logging.info("No 'ESCOLARIDADE' column found in the data.")
        except Exception as e:
            logging.error(f"Failed to create education data table: {e}")

        try:
            # Check if there is a column named 'PROFISSAO' or 'TRABALHO' and create the table for the top 10 professions
            prof_columns = ['PROFISSAO', 'TRABALHO']
            for prof_col in prof_columns:
                if prof_col in str_columns:
                    ten_prof_max = first_tenth(data, prof_col)
                    table_data = [[profession, count] for profession, count in ten_prof_max.items()]
                    headers = ['Profissão', 'Qtd']
                    column_widths_prof = [520, 80]  # Adjust column widths as needed
                    professions_table = make_table(table_data, headers, column_widths_prof)
                    report_dto.add_section("Table_Top 10 prof", professions_table)
                    added_sections.append("Table_Top 10 prof")
                    logging.info(f"Table_Top 10 prof table added.")

                    # Check if 'RENDA_PRESUMIDA' is also present and create the top 10 average income table
                    if 'RENDA_PRESUMIDA' in numeric_columns:
                        ten_mean_high = mean_and_count_by(data, prof_col, 'RENDA_PRESUMIDA')
                        ten_mean_high_filtered = ten_mean_high[ten_mean_high['count'] > 3]
                        top_ten = ten_mean_high_filtered.nlargest(10, 'mean')
                        table_data = [[row[prof_col], f"{row['mean']:.2f}", row['count']] for index, row in top_ten.iterrows()]
                        headers = ['Profissão', 'Renda Média', 'Qtd']
                        column_widths_renda = [420, 80, 50]  # Adjust column widths as needed
                        renda_mean_table = make_table(table_data, headers, column_widths_renda)
                        report_dto.add_section("Table_Top 10 prof_col by Renda", renda_mean_table)
                        added_sections.append("Table_Top 10 prof_col by Renda")
                        logging.info(f"Top 10 prof_col by average income table added.")
                        break  # Stop after the first match to avoid duplicate tables
                else:
                    logging.info(f"No '{prof_col}' column found in the data.")
        except Exception as e:
            logging.error(f"Failed to create top 10 professions or average income table: {e}")

        state_abbreviations = [
            'SP', 'RJ', 'MG', 'RS', 'PR', 'BA', 'PE', 'CE', 'SC', 'GO', 'PA',
            'PB', 'ES', 'MS', 'MA', 'RN', 'MT', 'AL', 'DF', 'PI', 'AM', 'SE',
            'RO', 'TO', 'AC', 'AP', 'RR'
        ]

        state_names = [
            'São Paulo', 'Rio de Janeiro', 'Minas Gerais', 'Rio Grande do Sul', 'Paraná', 'Bahia',
            'Pernambuco', 'Ceará', 'Santa Catarina', 'Goiás', 'Pará', 'Paraíba', 'Espírito Santo',
            'Mato Grosso do Sul', 'Maranhão', 'Rio Grande do Norte', 'Mato Grosso', 'Alagoas', 'Distrito Federal',
            'Piauí', 'Amazonas', 'Sergipe', 'Rondônia', 'Tocantins', 'Acre', 'Amapá', 'Roraima'
        ]

        try:
            # First check for columns named 'UF' or 'ESTADO'
            columns_to_plot = ['UF', 'ESTADO']
            columns_found = [col for col in columns_to_plot if col in str_columns]

            if columns_found:
                for column in columns_found:
                    cake_plot_path = cake_plot(data, column)
                    report_dto.add_section(f"Graph_Cake Plot for {column}", cake_plot_path)
                    graph_sections.append(f"Graph_Cake Plot for {column}")
                    logging.info(f"Graph_Cake Plot for {column} generated successfully. Path: {cake_plot_path}")

                    cake_plot_n_path = cake_plot_bigger_than_n(data, column, 3)
                    report_dto.add_section(f"Graph_Cake Plot for {column} (n=3)", cake_plot_n_path)
                    graph_sections.append(f"Graph_Cake Plot for {column} (n=3)")
                    logging.info(f"Graph_Cake Plot for {column} (n=3) generated successfully. Path: {cake_plot_n_path}")
            else:
                # If no 'UF' or 'ESTADO' columns found, check for any string column with at least 5 state values
                for column in str_columns:
                    unique_values = data[column].unique()
                    count_states = sum(1 for value in unique_values if value in state_abbreviations or value in state_names)
                    if count_states >= 5:
                        cake_plot_path = cake_plot(data, column)
                        report_dto.add_section(f"Graph_Cake Plot for {column}", cake_plot_path)
                        graph_sections.append(f"Graph_Cake Plot for {column}")
                        logging.info(f"Graph_Cake Plot for {column} generated successfully. Path: {cake_plot_path}")

                        cake_plot_n_path = cake_plot_bigger_than_n(data, column, 3)
                        report_dto.add_section(f"Graph_Cake Plot for {column} (n=3)", cake_plot_n_path)
                        graph_sections.append(f"Graph_Cake Plot for {column} (n=3)")
                        logging.info(f"Graph_Cake Plot for {column} (n=3) generated successfully. Path: {cake_plot_n_path}")
        except Exception as e:
            logging.error(f"Failed to generate cake plots for state columns: {e}")
            report_dto.add_section("Graph_Cake Plot for State Columns", "Graph generation failed")

        try:
            # Combine int and float columns, convert to float for correlation plot
            correlation_plot_path = generate_correlation_plot(data, numeric_columns)
            report_dto.add_section("Graph_Correlation Plot", correlation_plot_path)
            graph_sections.append("Graph_Correlation Plot")
        except Exception as e:
            logging.error(f"Failed to generate correlation plot: {e}")

        try:
            # Set the order of sections in the report
            report_dto.set_order(added_sections + graph_sections)
        except Exception as e:
            logging.error(f"Failed to set the order of sections in the report: {e}")

        return report_dto

    def split_text_into_lines(self, text, max_length):
        words = text.split(', ')
        lines = []
        current_line = []

        for word in words:
            if len(', '.join(current_line + [word])) > max_length:
                lines.append(', '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)

        if current_line:
            lines.append(', '.join(current_line))

        return lines



        # Generate Bar Plots for columns with less than 3 unique values



        # # Generate Bar Plots for columns with less than 3 unique values
        # for col in data.columns:
        #     unique_values = data[col].nunique()
        #     if unique_values < 3:
        #         self.generate_bar_plot(data, col, report_dto)



        # report_dto.add_section("Introdução", intro)
        # report_dto.add_section("Hábitos de Consumo", habitos_consumo)
        # report_dto.add_section("Consumo Telefónico Geral", consumo_geral)
        # report_dto.add_section("Consumo Digital", consumo_digital)
        #
        #
        # report_dto.add_section("Dez profissões que mais existem", professions_table)
        # report_dto.add_section("Tabela de Renda Meia mais de 3850", Renda_mean_table_abv_100)
        # report_dto.add_section("Tabela de Renda Meia mais grande", Renda_mean_higher_table)
        #
        # report_dto.add_section("Educacão", Educacão)
        # report_dto.add_section("Tabela de Educação", education_table)
        #
        #
        # # Gerando e adicionando gráficos
        # try:
        #     data['Faixa Idade'] = data['edad'].apply(map_age_to_range)
        #     idade_chart_path = cake_plot(data, 'Faixa Idade', title='Distribuição das Faixas Etárias')
        #     report_dto.add_section("Graph_Faixa_Edades", idade_chart_path)
        # except Exception as e:
        #     print(f"Falha ao gerar gráfico de faixa etária: {e}")

        # try:
        #     estado_civil_graph_path = bar_plot(data, 'ESTCIV')
        #     report_dto.add_section("Graph_ESTADO_CIVIL", estado_civil_graph_path)
        # except Exception as e:
        #     print(f"Falha ao gerar gráfico de estado civil: {e}")
        #
        # poder_aquisitivo_map = {
        #     1: 'MUITO BAIXO',
        #     2: 'BAIXO',
        #     3: 'MEDIO BAIXO',
        #     4: 'MEDIO',
        #     5: 'MEDIO ALTO',
        #     6: 'ALTO',
        #     7: 'MUITO ALTO'
        # }
        #
        # # Apply the mapping to the 'COD_PODER_AQUISITIVO' column
        # data['PODER_AQUISITIVO'] = data['COD_PODER_AQUISITIVO'].map(poder_aquisitivo_map)
        #
        # try:
        #     classe_social_chart_path = cake_plot(data, 'PODER_AQUISITIVO', title='Distribuição de Classe Social')
        #     report_dto.add_section("Graph_Classe_Social", classe_social_chart_path)
        # except Exception as e:
        #     print(f"Falha ao gerar gráfico de classe social: {e}")
        #
        # try:
        #     uf_graph_path = cake_plot_bigger_than_n(data, 'UF', 1, title='Distribuição UFs encima 1%')
        #     report_dto.add_section("Graph_UF", uf_graph_path)
        # except Exception as e:
        #     print(f"Falha ao gerar gráfico de uf: {e}")
        #

        #     multicolumns_bar_consumo_path = multicolumns_bar_plot(data, flag_columns_consumo)
        #     report_dto.add_section("Graph_Consumo_Bar", multicolumns_bar_consumo_path)
        # except Exception as e:
        #     print(f"Falha ao gerar gráfico de consumo: {e}")
        #
        # try:
        #     flag_columns_internet = [
        #         'INTERNET_BANKING',
        #         'BANDA_LARGA',
        #         'E_COMMERCE',
        #         'INTERNET_HIGH_USER',
        #         'LEITOR_DIGITAL']
        #     multicolumns_bar_credito_path = multicolumns_bar_plot(data, flag_columns_internet)
        #     report_dto.add_section("Graph_Internet", multicolumns_bar_credito_path)
        # except Exception as e:
        #     print(f"Falha ao gerar gráfico de crédito: {e}")
        #
        # try:
        #     heatmap_path = generate_heatmap(data, 'CIDADE')
        #     report_dto.add_section("Graph_CIDADE_Heatmap", heatmap_path)
        # except Exception as e:
        #     print(f"Failed to generate heatmap for 'BAIRRO': {e}")
        #
        # # Definindo a ordem das seções no relatório
        # report_dto.set_order([
        #     "Introdução", "Descrição dos Dados", "Graph_Faixa_Edades", "Graph_SEXO", "Graph_ESTADO_CIVIL",
        #     "Graph_Classe_Social", "Análise dos Gráficos Iniciais",
        #
        #     "Hábitos de Consumo", "Graph_Consumo_Bar", "Consumo Telefónico Geral", "Graph_Internet", "Consumo Digital"
        #
        #     , "Renda", "Dez profissões que mais existem", "Tabela de Renda Meia mais de 3850",
        #     "Tabela de Renda Meia mais grande",
        #
        #     "Dados Demográficos", "Graph_UF", "Graph_CIDADE_Heatmap",
        #
        #     "Tabela de Educação", "Educacão"
        #
        # ])

        #return report_dto

#%%
