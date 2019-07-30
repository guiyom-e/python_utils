# -*- coding: utf-8 -*-
# open source project
"""
Simple functions to manipulate dataframes with a user interface.
"""
import pandas as pd
from collections import OrderedDict

from tools.logger import logger
from tools.helpers.interface import simpledialog, messagebox


# Selections
def dataframe_column_selection(df):
    """Select certain certain columns of a dataframe"""
    columns = list(df.columns)
    columns_to_filter = simpledialog.ask_multiple_questions(message="Select the columns to keep",
                                                            initial_status=False,
                                                            choices={'columns': columns})
    if columns_to_filter is None:
        return df
    columns_to_filter = columns_to_filter['columns']
    n_df = df[columns_to_filter]
    return n_df


def dataframe_values_selection(df, columns):
    """Select certain lines of a dataframe considering specific values of certain columns"""
    columns = [columns] if isinstance(columns, str) else columns
    choices = OrderedDict([(col, sorted(set(df[col]))) for col in columns if col in df.columns])
    res = simpledialog.ask_multiple_questions(message="Select the values to keep", choices=choices)
    for col, values in res.items():
        df = df[df[col].isin(values)]
    return df


# Group by
def dataframe_groupby(df, synthesis_col=None, agg_dict=None, agg_methods=None):
    """Group by the columns selected by the user."""
    columns = list(df.columns)
    agg_methods = agg_methods or ['first', 'last', 'count', 'nunique', 'sum', 'mean', 'min', 'max']
    synthesis_col = synthesis_col or df.columns

    choices = OrderedDict([('columns_to_group', {'choices': columns, 'name': 'Columns to group'}),
                           ('agg_methods', {'choices': agg_methods, 'name': 'Aggregation methods',
                                            'initial_status': True}),
                           ('synt_columns', {'choices': synthesis_col, 'name': 'Columns to aggregate',
                                             'initial_status': True}),
                           ])
    res = simpledialog.ask_multiple_questions(message="Select the columns to group",
                                              initial_status=False,
                                              choices=choices)
    if res is None:
        return df
    columns_to_group = res['columns_to_group']
    agg_methods = res['agg_methods'] or 'last'
    synthesis_col = res['synt_columns']
    if not columns_to_group:
        return df
    agg_dict = agg_dict or {col: agg_methods for col in synthesis_col if col not in columns_to_group}
    n_df = df.groupby(columns_to_group).agg(agg_dict).reset_index()
    return n_df


# Simple analysis
def dataframe_describe(df, columns=None):
    """Apply describe method to certain columns of a dataframe"""
    if columns is None:
        columns = df.columns
    else:
        columns = [columns] if isinstance(columns, str) else columns
        columns = [ele for ele in columns if ele in df.columns]
    res = df[columns].describe().round(2)
    return res


def dataframe_quick_analysis(df):
    """Filter certain columns and aggregate results."""
    df = dataframe_column_selection(df)
    columns_to_filter = simpledialog.ask_multiple_questions(message="Select columns to filter",
                                                            initial_status=False,
                                                            choices={'columns': list(df.columns)})
    if columns_to_filter and columns_to_filter['columns']:
        df = dataframe_values_selection(df, columns_to_filter['columns'])
    df = dataframe_groupby(df)
    messagebox.showtext(title="Dataframe description", text=df)
    return df


if __name__ == '__main__':
    _df = pd.DataFrame(columns=['week', 'year', 'station'],
                       data=[[1, 2018, 0], [10, 2018, 0], [53, 2018, 0], [1, 2019, 0], [5, 2019, 0], [52, 2019, 0]])
    print(dataframe_column_selection(_df))
    print(dataframe_values_selection(_df, ['week', 'year', 'station']))
    print(dataframe_groupby(_df))
    messagebox.showtext(title="Dataframe preview", text=_df)
    print(dataframe_quick_analysis(_df))
