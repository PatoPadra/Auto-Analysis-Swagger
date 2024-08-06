import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import logging

def cake_plot(df, column, base_dir='/Domain/Relatorio/Functions/Graphs/tempt-graphs', title='Pie Chart', labels_map=None):
    # Ensure the directory exists
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # If a labels map is provided, use it to replace the labels in the DataFrame
    if labels_map:
        df[column] = df[column].map(labels_map)

    # Count the occurrences of each class
    value_counts = df[column].value_counts()

    # Sort the value_counts according to labels_map order
    if labels_map:
        value_counts = value_counts.reindex(labels_map.values())

    # Define a larger set of colors for each slice
    colors = plt.cm.tab20(np.linspace(0, 1, len(value_counts)))

    # Create the pie chart with a larger figure size
    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, pct_texts = ax.pie(value_counts, labels=None, autopct='%1.1f%%', startangle=140, colors=colors)

    dynamic_legend_title = title
    if 'Distribuição' in title:
        try:
            dynamic_legend_title = title.split('Distribuição')[1].strip()
        except IndexError:
            logging.error(f"Failed to split title properly: {title}")

    # Add a legend outside of the pie chart with the descriptive labels and counts
    labels = [f'{label}: {count}' for label, count in zip(value_counts.index, value_counts.sort_values(ascending=False))]
    plt.legend(wedges, labels, title=dynamic_legend_title, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    # Set the aspect ratio to be equal, so the pie is drawn as a circle.
    ax.axis('equal')

    plt.title(title)
    plt.tight_layout()
    fig.patch.set_facecolor('white')  # Set the background color of the figure to white

    # Save the plot
    file_path = f'{base_dir}/{column}_cake_chart.png'
    plt.savefig(file_path, bbox_inches='tight')  # Use bbox_inches='tight' to fit the plot neatly
    plt.close()

    return file_path


# import matplotlib
# matplotlib.use('Agg')  # Use a non-interactive backend
# import matplotlib.pyplot as plt
# import numpy as np
# import os
# import pandas as pd
#
# def cake_plot(df, column, base_dir='/Domain/Relatorio/Functions/Graphs/tempt-graphs', title='Pie Chart', labels_map=None):
#     # Ensure the directory exists
#
#
#     if not os.path.exists(base_dir):
#         os.makedirs(base_dir)
#
#     # If a labels map is provided, use it to replace the labels in the DataFrame
#     if labels_map:
#         df[column] = df[column].map(labels_map)
#
#     # Count the occurrences of each class
#     value_counts = df[column].value_counts()
#
#     # Sort the value_counts according to labels_map order
#     if labels_map:
#         value_counts = value_counts.reindex(labels_map.values())
#
#     # Define a larger set of colors for each slice
#     colors = plt.cm.tab20(np.linspace(0, 1, len(value_counts)))
#
#     # Create the pie chart with a larger figure size
#     fig, ax = plt.subplots(figsize=(8, 6))
#     wedges, texts, pct_texts = ax.pie(value_counts, labels=None, autopct='%1.1f%%', startangle=140, colors=colors)
#
#     dynamic_legend_title = title.split('Distribuição')[1].strip()
#
#     # Add a legend outside of the pie chart with the descriptive labels and counts
#     labels = [f'{label}: {count}' for label, count in zip(value_counts.index, value_counts.sort_values(ascending=False))]
#     plt.legend(wedges, labels, title=dynamic_legend_title, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
#
#     # Set the aspect ratio to be equal, so the pie is drawn as a circle.
#     ax.axis('equal')
#
#     plt.title(title)
#     plt.tight_layout()
#     fig.patch.set_facecolor('white')  # Set the background color of the figure to white
#
#     # Save the plot
#     file_path = f'{base_dir}/{column}_cake_chart.png'
#     plt.savefig(file_path, bbox_inches='tight')  # Use bbox_inches='tight' to fit the plot neatly
#     plt.close()
#
#     return file_path