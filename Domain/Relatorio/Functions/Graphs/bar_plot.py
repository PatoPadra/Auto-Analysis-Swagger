import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
import os

def bar_plot(df, column, base_dir='Domain/Relatorio/Functions/Graphs/temp - graphs'):
    # Ensure the directory exists
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # Convert boolean values to strings to avoid plotting issues
    if df[column].dtype == 'bool':
        df[column] = df[column].astype(str)

    # Prepare the data
    value_counts = df[column].value_counts()
    percentages = (value_counts / len(df) * 100).round(2)  # Calculate percentages, rounded to 2 decimal places

    # Create the plot
    plt.figure(figsize=(6, 4))
    bars = plt.bar(value_counts.index, value_counts.values, color=plt.cm.Paired(range(len(value_counts))))

    # Add counts inside the bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, f'{int(yval)}', va='top', ha='center', color='white', fontsize=9)

    # Add percentage labels above the bars
    for idx, percentage in zip(value_counts.index, percentages):
        plt.text(idx, value_counts.loc[idx], f'{percentage}%', va='bottom', ha='center', color='black', fontsize=9)

    plt.title(f'Bar plot of {column}')
    plt.xticks(rotation=45)  # Rotate category labels for better readability
    plt.ylabel('Counts')

    # Save the plot
    file_path = os.path.join(base_dir, f'{column}_graph.png')
    plt.savefig(file_path, bbox_inches='tight')  # Use bbox_inches='tight' to fit the plot neatly
    plt.close()

    # Print the path for debugging
    print(f"Bar plot saved to: {file_path}")

    return file_path
