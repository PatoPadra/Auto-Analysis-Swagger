

def calculate_stats(df, column):
    counts = df[column].value_counts()
    percentages = (counts / counts.sum()) * 100

    if counts.empty:
        return counts, percentages, None, None, None

    highest = counts.idxmax()

    if len(counts) == 1:
        second_highest = None
        third_highest = None
    else:
        second_highest = counts.drop(highest).idxmax()
        if len(counts) == 2:
            third_highest = None
        else:
            third_highest = counts.drop([highest, second_highest]).idxmax()

    return counts, percentages, highest, second_highest, third_highest


def first_tenth(df, column):
    counts = df[column].value_counts()
    return counts.head(10)

def mean_and_count_by(df, group, mean_column):
    result = df.groupby(group)[mean_column].agg(['mean', 'count'])
    result.reset_index(inplace=True)
    result['mean'] = result['mean'].round(2)  # Round the mean income values for better display
    return result


def filtered_by_word(df, column, word):
    """
    Filter the DataFrame based on the presence of a word in a specified column.
    :param df: The input DataFrame.
    :param column: The column to search for the word.
    :param word: The word to filter by.
    :return: A filtered DataFrame.
    """
    return df[df[column].str.contains(word, case=False, na=False)]




