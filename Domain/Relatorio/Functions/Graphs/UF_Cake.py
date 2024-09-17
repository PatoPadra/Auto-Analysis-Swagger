import logging
from .cake_plot import cake_plot
from .cake_plot_bigger_than_n import cake_plot_bigger_than_n


# Define state abbreviations and names
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

def Have_UF_Info(data, str_columns):
    """
    Checks for the presence of 'UF' or 'ESTADO' columns or state values in other string columns.
    """
    columns_to_plot = ['UF', 'ESTADO']
    columns_found = [col for col in columns_to_plot if col in str_columns]

    if not columns_found:
        # If no 'UF' or 'ESTADO' columns found, check for any string column with at least 5 state values
        for column in str_columns:
            unique_values = data[column].unique()
            count_states = sum(1 for value in unique_values if value in state_abbreviations or value in state_names)
            if count_states >= 5:
                columns_found.append(column)
                break

    return columns_found

def UF_Cake_All(data, report_dto, graph_sections, columns_found):
    """
    Generates the regular cake plot for columns containing 'UF' or 'ESTADO' or having state values.
    """
    for column in columns_found:
        cake_plot_path = cake_plot(data, column)
        report_dto.add_section(f"Graph_Cake Plot for {column}", cake_plot_path)
        graph_sections.append(f"Graph_Cake Plot for {column}")
        logging.info(f"Graph_Cake Plot for {column} generated successfully. Path: {cake_plot_path}")

def UF_Cake_Filtered(data, report_dto, graph_sections, columns_found, n=5):
    """
    Generates the filtered cake plot (greater than n%) for columns containing 'UF' or 'ESTADO' or having state values.
    """
    for column in columns_found:
        cake_plot_n_path = cake_plot_bigger_than_n(data, column, n)
        report_dto.add_section(f"Graph_Cake Plot for {column} (n={n})", cake_plot_n_path)
        graph_sections.append(f"Graph_Cake Plot for {column} (n={n})")
        logging.info(f"Graph_Cake Plot for {column} (n={n}) generated successfully. Path: {cake_plot_n_path}")
