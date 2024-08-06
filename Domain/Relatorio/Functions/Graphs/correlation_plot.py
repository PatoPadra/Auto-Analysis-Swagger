import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


def generate_correlation_plot(df, columns, output_dir='Domain/Relatorio/Functions/Graphs/temp - graphs'):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Select the specified columns and convert them to float
    df_selected = df[columns].astype(float)

    # Drop rows with NaN values
    df_selected = df_selected.dropna()

    # Proceed with the correlation and plotting
    df_corr = df_selected.corr(method='spearman')

    # Create a mask for the upper triangle
    mask = np.triu(np.ones_like(df_corr, dtype=bool))

    # Set up the matplotlib figure
    fig, ax = plt.subplots(figsize=(12, 12))  # Adjust as needed for your PDF

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(df_corr, mask=mask, vmax=0.9, square=True, annot=True,
                fmt=".2f", annot_kws={"size": 12}, cmap='coolwarm')  # Increase annot_kws size as needed

    # Set the font size for the axes labels
    plt.xticks(fontsize=12)  # Increase x-axis labels font size
    plt.yticks(fontsize=12)  # Increase y-axis labels font size

    # Improve layout and adjust for the plot to fit well within the figure area
    plt.tight_layout()

    # Save the plot
    plot_path = os.path.join(output_dir, 'correlation_plot.png')
    plt.savefig(plot_path)
    plt.close()

    return plot_path
