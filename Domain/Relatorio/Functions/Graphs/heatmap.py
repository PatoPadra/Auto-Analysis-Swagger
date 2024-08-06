import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import uuid

def generate_heatmap(df, column, min_count=10, base_dir='/Domain/Relatorio/Functions/Graphs/tempt-graphs'):
    """
    Generate a heatmap for the specified column in the DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing the data.
    column (str): Column name for which to generate the heatmap.
    min_count (int): Minimum count to include in the heatmap.
    base_dir (str): Directory to save the generated heatmap.

    Returns:
    str: Path to the saved heatmap image.
    """
    # Ensure the directory exists
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # Step 1: Calculate the value counts for the specified column
    value_counts = df[column].value_counts()

    # Step 2: Filter the counts to include only those that are greater than or equal to min_count
    value_counts_filtered = value_counts[value_counts >= min_count]

    # Step 3: Sort the filtered counts from highest to lowest and take the top 10
    value_counts_filtered_sorted = value_counts_filtered.sort_values(ascending=False).head(10)

    # Step 4: Create a DataFrame suitable for a heatmap
    heatmap_data = pd.DataFrame(value_counts_filtered_sorted).reset_index()
    heatmap_data.columns = [column, 'COUNT']

    # Step 5: Create the heatmap using Seaborn
    plt.figure(figsize=(12, 15))
    heatmap_data_sorted = heatmap_data.sort_values('COUNT', ascending=False)

    sns.heatmap(
        heatmap_data_sorted[['COUNT']],
        annot=True,
        fmt='d',
        cmap='viridis',
        cbar_kws={'label': 'Count'},
        yticklabels=heatmap_data_sorted[column]
    )
    plt.title(f'{column} Value Counts Heatmap')
    plt.ylabel(column)

    # Generate a unique filename using uuid
    unique_filename = f'heatmap_{column}_{uuid.uuid4().hex}.png'
    file_path = os.path.join(base_dir, unique_filename)

    plt.savefig(file_path, bbox_inches='tight')
    plt.close()

    return file_path
