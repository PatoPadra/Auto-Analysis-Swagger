def multicolumns_bar_plot(df, columns, base_dir='/Domain/Relatorio/Functions/Graphs/tempt-graphs'):
    import matplotlib.pyplot as plt
    import numpy as np
    import os
    import pandas as pd
    import uuid

    # Ensure the directory exists
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # Calculate percentages and counts
    percentages = df[columns].mean() * 100
    counts = df[columns].sum()

    # Prepare the DataFrame for plotting
    plot_data = pd.DataFrame({'Flag': columns, 'Percentage': percentages, 'Count': counts})

    # Sort the data for better visualization
    plot_data.sort_values('Percentage', ascending=False, inplace=True)

    # Create the bar plot with a larger figure size
    fig, ax = plt.subplots(figsize=(26,22))

    # Plot the bars with counts inside and percentages above
    bars = ax.bar(plot_data['Flag'], plot_data['Percentage'], color=plt.cm.tab10(np.arange(len(plot_data))))

    # Add the percentage above the bars
    for bar, percentage in zip(bars, plot_data['Percentage']):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{percentage:.1f}%',
                ha='center', va='bottom', color='black', fontsize=10)

    # Add the count inside the bars
    for bar, count in zip(bars, plot_data['Count']):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2, str(count),
                ha='center', va='center', color='white', fontsize=10)

    # Set labels and title
    ax.set_xlabel('Flag', color='black')
    ax.set_ylabel('(%)', color='black')
    ax.set_title('Porcentagem de valores verdadeiros', color='black')

    # Set the background color of the figure to white
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Remove x-axis labels for neatness
    plt.xticks(rotation=90)

    plt.tight_layout()

    # Generate a unique filename using uuid
    unique_filename = f'multicolumns_bar_chart_{uuid.uuid4().hex}.png'
    file_path = os.path.join(base_dir, unique_filename)

    plt.savefig(file_path, bbox_inches='tight')  # Save the figure
    plt.close()

    return file_path
