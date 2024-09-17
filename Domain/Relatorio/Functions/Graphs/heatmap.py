import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import uuid

def generate_heatmap(df, column, base_dir='/Domain/Relatorio/Functions/Graphs/tempt-graphs', title=None, min_count=10):
    """
    Generate a heatmap for the specified column in the DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing the data.
    column (str): Column name for which to generate the heatmap.
    base_dir (str): Directory to save the generated heatmap.
    title (str): Title of the heatmap.
    min_count (int): Minimum count to include in the heatmap.

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
    sns.heatmap(
        heatmap_data.pivot_table(index=column, values='COUNT'),
        annot=True,
        fmt='d',
        cmap='viridis',
        cbar_kws={'label': 'Count'}
    )

    # Set the title with the column name
    plt.title(f'{title if title else column} Value Counts Heatmap')
    plt.ylabel(column)

    # Generate a unique filename using uuid
    unique_filename = f'heatmap_{column}_{uuid.uuid4().hex}.png'
    file_path = os.path.join(base_dir, unique_filename)

    plt.tight_layout()
    fig = plt.gcf()
    fig.patch.set_facecolor('white')  # Set the background color of the figure to white

    plt.savefig(file_path, bbox_inches='tight')
    plt.close()

    return file_path
