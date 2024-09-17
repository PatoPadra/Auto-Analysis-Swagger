import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import os
import logging
import seaborn as sns

def cake_plot_bigger_than_n(df, column, n, base_dir='/Domain/Relatorio/Functions/Graphs/tempt-graphs', title=None, labels_map=None):
    # Ensure the directory exists
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # If a labels map is provided, use it to replace the labels in the DataFrame
    if labels_map:
        df[column] = df[column].map(labels_map)

    # Count the occurrences of each class
    value_counts = df[column].value_counts()

    # Calculate percentages
    total_count = value_counts.sum()
    percentages = (value_counts / total_count) * 100

    # Filter to keep only values with percentages greater than or equal to n
    filtered_counts = value_counts[percentages >= n]
    filtered_percentages = percentages[percentages >= n]

    # Sort the filtered_counts according to labels_map order if labels_map is provided
    if labels_map:
        filtered_counts = filtered_counts.reindex(labels_map.values())

    # Generate a color list using Seaborn color palette
    colors = sns.color_palette("dark", len(filtered_counts))

    # Create the pie chart with a larger figure size
    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, pct_texts = ax.pie(filtered_counts, labels=None, autopct='%1.1f%%', startangle=140, colors=colors)

    dynamic_legend_title = title if title else f"{column} (n > {n})"
    if 'Distribuição' in dynamic_legend_title:
        try:
            dynamic_legend_title = dynamic_legend_title.split('Distribuição')[1].strip()
        except IndexError:
            logging.error(f"Failed to split title properly: {title}")

    # Add a legend outside of the pie chart with the descriptive labels and counts
    labels = [f'{label}: {count} ({percentage:.1f}%)' for label, count, percentage in zip(filtered_counts.index, filtered_counts, filtered_percentages)]
    plt.legend(wedges, labels, title=dynamic_legend_title, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    # Set the aspect ratio to be equal, so the pie is drawn as a circle.
    ax.axis('equal')

    # Set the title with the column name and n value
    plt.title(f"{column} Distribution (≥ {n}%)")

    plt.tight_layout()
    fig.patch.set_facecolor('white')  # Set the background color of the figure to white

    # Save the plot with a unique identifier for the regular cake plot
    file_path = f'{base_dir}/{column}_cake_chart_n{n}.png'
    plt.savefig(file_path, bbox_inches='tight')  # Use bbox_inches='tight' to fit the plot neatly
    plt.close()

    return file_path
