from ..DTO.relatorioDTO import ReportDTO
from .Functions.Tables.Education import make_education_table
from .Functions.Tables.Work import make_work_table
from .Functions.Tables.Renda import make_renda_table_more_than_three, make_greater_renda_table
from .Functions.Tables.Unique import make_unique_values_table
from .Functions.Graphs.UF_Cake import Have_UF_Info, UF_Cake_All, UF_Cake_Filtered
from .Functions.Statics.Column_Transform import Data_info_and_transform
from .Functions.Statics.data_process import Checking_IDS
from .Functions.Graphs.heatmap import generate_heatmap
from .Functions.Graphs.bar_plot import bar_plot
from .Functions.Graphs.correlation_plot import generate_correlation_plot
from ..Get_data import fetch_data_from_sql
from .Functions.Statics.Stats import calculate_stats,filtered_by_word


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

    def create_report(self, server, database, table):
        report_dto = ReportDTO()
        graph_sections = []
        added_sections = []

        # Fetch data and table name
        data, table_name = fetch_data_from_sql(server, database, table)

        # Perform data info capture and transformation
        data, int_columns, float_columns, str_columns, bool_columns = Data_info_and_transform(
            data, report_dto, added_sections, table=table_name)

        try:
            # Create unique values table
            make_unique_values_table(data, report_dto, added_sections)
        except Exception as e:
            logging.error(f"Failed to create unique values count table: {e}")

        try:
            # Check for possible ID columns
            ids_columns = Checking_IDS(data, report_dto, added_sections)

            # You can use `ids_columns` further in your script if needed
            if ids_columns:
                logging.info(f"Possible ID columns identified: {ids_columns}")
            else:
                logging.info("No possible ID columns identified.")
        except Exception as e:
            logging.error(f"An error occurred while checking for ID columns: {e}")

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
                make_education_table(data, report_dto, added_sections, column='ESCOLARIDADE')
            else:
                logging.info("No 'ESCOLARIDADE' column found in the data.")
        except Exception as e:
            logging.error(f"Failed to create education data table: {e}")

        try:
            # Check if there is a column named 'PROFISSAO' or 'TRABALHO' and create the table for the top 10 professions
            prof_columns = ['PROFISSAO', 'TRABALHO']
            for prof_col in prof_columns:
                if prof_col in str_columns:
                    make_work_table(data, report_dto, added_sections, column=prof_col)

                    # Check if 'RENDA_PRESUMIDA' is also present and create the top 10 average income table
                    if 'RENDA_PRESUMIDA' in numeric_columns:
                        # Add summary statistics for 'RENDA_PRESUMIDA'
                        renda_description = data['RENDA_PRESUMIDA'].describe().to_string()
                        report_dto.add_section("RENDA_PRESUMIDA Summary Statistics", renda_description)
                        added_sections.append("RENDA_PRESUMIDA Summary Statistics")

                        make_renda_table_more_than_three(data, report_dto, added_sections, prof_col, numeric_column='RENDA_PRESUMIDA')
                        make_greater_renda_table(data, report_dto, added_sections, prof_col, numeric_column='RENDA_PRESUMIDA')
                    break  # Stop after the first match to avoid duplicate tables

                else:
                    logging.info(f"No '{prof_col}' column found in the data.")
        except Exception as e:
            logging.error(f"Failed to create top 10 professions or average income table: {e}")

        try:
            # Check if there are columns with 'UF' or 'ESTADO' or containing state info
            columns_found = Have_UF_Info(data, str_columns)

            if columns_found:
                # Generate all UF cake plots
                UF_Cake_All(data, report_dto, graph_sections, columns_found)

                # Check if any percentages in 'columnuf' are below 5% before generating filtered UF cake plots
                percentages = data[columns_found].value_counts(normalize=True)

                if percentages.lt(0.05).any():
                    # If there are any percentages below 5%, call UF_Cake_Filtered
                    UF_Cake_Filtered(data, report_dto, graph_sections, columns_found, n=5)
                else:
                    logging.info(f"No percentages below 5% for column {columns_found}. Skipping UF_Cake_Filtered.")

                # Check if the 'CIDADE' column exists
                if 'CIDADE' in str_columns:
                    # Calculate stats for the 'UF' column
                    counts, percentages, highest, second_highest, third_highest = calculate_stats(data, 'UF')

                    # Filter the data for the highest, second_highest, and third_highest 'UF' values
                    if highest:
                        filtered_highest = filtered_by_word(data, 'UF', highest)
                        heatmap_path = generate_heatmap(filtered_highest, 'CIDADE', title=f"Heatmap for {highest}")
                        report_dto.add_section(f"Heatmap_CIDADE_{highest}", heatmap_path)
                        graph_sections.append(f"Heatmap_CIDADE_{highest}")
                    if second_highest:
                        filtered_second_highest = filtered_by_word(data, 'UF', second_highest)
                        heatmap_path = generate_heatmap(filtered_second_highest, 'CIDADE', title=f"Heatmap for {second_highest}")
                        report_dto.add_section(f"Heatmap_CIDADE_{second_highest}", heatmap_path)
                        graph_sections.append(f"Heatmap_CIDADE_{second_highest}")
                    if third_highest:
                        filtered_third_highest = filtered_by_word(data, 'UF', third_highest)
                        heatmap_path = generate_heatmap(filtered_third_highest, 'CIDADE', title=f"Heatmap for {third_highest}")
                        report_dto.add_section(f"Heatmap_CIDADE_{third_highest}", heatmap_path)
                        graph_sections.append(f"Heatmap_CIDADE_{third_highest}")
                else:
                    logging.info("No 'CIDADE' column found.")
            else:
                logging.info("No 'UF' or 'ESTADO' columns found or no columns with state values.")
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
