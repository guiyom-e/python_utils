# -*- coding: utf-8 -*-
# open source project
"""
Simple functions to manipulate dataframes with a user interface:
- Select columns to keep with dataframe_column_selection
- Select rows with certain values to keep with dataframe_values_selection
- Aggregate a table with dataframe_groupby
- Get a simple description of the dataframe with dataframe_describe
- Get a description of aggregated data with dataframe_quick_analysis
- Merge dataframes with different methods with dataframe_merge
"""
import pandas as pd
from collections import OrderedDict
from typing import Union

from tools.logger import logger
from tools.helpers.interface import simpledialog, messagebox
from tools.helpers.models import IdentityDict


# Selections
def dataframe_column_selection(df, multiple_selection=True) -> Union[pd.DataFrame, pd.Series]:
    """Select certain certain columns of a dataframe"""
    columns = list(df.columns)
    box_type = 'check_box' if multiple_selection else 'radio'
    columns_to_filter = simpledialog.ask_multiple_questions(message="Select the columns to keep",
                                                            initial_status=False,
                                                            choices={'columns': columns},
                                                            default_box_type=box_type)
    if columns_to_filter is None:
        return df
    columns_to_filter = columns_to_filter['columns']
    n_df = df[columns_to_filter]
    return n_df


def dataframe_values_selection(df, columns=None):
    """Select certain lines of a dataframe considering specific values of certain columns"""
    columns = df.columns if columns is None else [columns] if isinstance(columns, str) else columns
    choices = OrderedDict()
    for col in columns:
        if col not in df.columns:
            continue
        col_type = df[col].dtype
        if col_type in ('int64', 'float64'):
            choices[col] = {'choices': sorted(set(df[col])), 'box_type': 'check_box'}
        elif col_type == 'datetime64[ns]':
            choices[col] = {'choices': sorted(set(df[col])), 'box_type': 'date_picker'}
        else:
            choices[col] = {'choices': list(set(df[col])), 'box_type': 'check_box'}
    res = simpledialog.ask_multiple_questions(message="Select the values to keep", choices=choices)
    if res is None:
        return None
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


def dataframe_merge(df1, df2, how_methods='outer', **kwargs):
    """Merge two dataframes

    :param df1: left dataframe
    :param df2: right dataframe
    :param how_methods: string or list of strings in 'outer', 'inner', 'left' or 'right'
    :param kwargs: keyword arguments for pandas.merge method
    :return: list of merged dataframes
    """
    choices = OrderedDict([
        ('ind_col1', {'name': "Columns of the first table to match",
                      'choices': df1.columns,
                      'box_type': 'radio'}),
        ('ind_col2', {'name': "Columns of the second table to match",
                      'choices': df2.columns,
                      'box_type': 'radio'}),
        ('cols1', {'name': "Columns of the first table to keep",
                   'choices': df1.columns,
                   'initial_status': True,
                   'box_type': 'check_box'}),
        ('cols2', {'name': "Columns of the second table to keep",
                   'choices': df2.columns,
                   'initial_status': True,
                   'box_type': 'check_box'}),
    ])
    cols_to_match = simpledialog.ask_multiple_questions(title="Columns to match",
                                                        message="Select the columns to match in order to merge tables",
                                                        choices=choices)
    if cols_to_match is None:
        logger.error("Choice of columns to match cancelled by user")
        return None
    ind_col1 = cols_to_match['ind_col1']
    ind_col2 = cols_to_match['ind_col2']
    cols1 = cols_to_match['cols1']
    cols2 = cols_to_match['cols2']
    kwargs['suffixes'] = kwargs.get('suffixes', ('_1', '_2'))
    cols_both_sides = set(df1.columns) & set(df2.columns) - ({ind_col1} & {ind_col2})

    # Manage columns with suffixes
    cols1_with_suffix = cols_both_sides & set(cols1)
    cols2_with_suffix = cols_both_sides & set(cols2)
    cols_still_both_sides = set(cols1_with_suffix) & set(cols2_with_suffix)
    cols1_with_suffix_unique = cols1_with_suffix - cols_still_both_sides
    cols2_with_suffix_unique = cols2_with_suffix - cols_still_both_sides

    all_cols_dict = IdentityDict({col: str(col) + kwargs['suffixes'][i]
                                  for i in (0, 1) for col in (cols1_with_suffix, cols2_with_suffix)[i]})
    all_cols = [all_cols_dict[col] for col in cols1 + cols2]
    rename_cols_dict = {str(col) + kwargs['suffixes'][i]: col
                        for i in (0, 1) for col in (cols1_with_suffix_unique, cols2_with_suffix_unique)[i]}

    how_methods = [how_methods] if isinstance(how_methods, str) else how_methods
    dfs = []
    for how in how_methods:
        try:
            m_df = pd.merge(df1, df2, left_on=ind_col1, right_on=ind_col2, how=how, **kwargs)
        except ValueError as err:
            err_msg = "Impossible to merge dataframes with method '{}' on '{}' and '{}'".format(how, ind_col1, ind_col2)
            logger.exception(err)
            logger.error(err_msg)
            continue
        m_df = m_df[all_cols]
        m_df.rename(columns=rename_cols_dict, inplace=True)
        dfs.append(m_df)
    return dfs


if __name__ == '__main__':
    from datetime import datetime as dt

    _df = pd.DataFrame(columns=['week', 'year', 'station'],
                       data=[['W3', 2018, 0], [10, 2018, 1], [53, 2018, 2], [1, 2019, 0], [5, 2019, 1], [52, 2019, 2]])
    _df2 = pd.DataFrame(columns=['station', 'train', 'date'],
                        data=[[1, 'tgv'], [1, 'rer', dt.now()], [2, 'transilien', dt(2019,5, 4)], [3, 'ter', pd.NaT],
                              [4, 'eurostar', dt(2019,5, 4)]])
    print(dataframe_column_selection(_df))
    print(dataframe_values_selection(_df, ['week', 'year', 'station']))
    print(dataframe_values_selection(_df2))
    print(dataframe_groupby(_df))
    messagebox.showtext(title="Dataframe preview", text=_df)
    print(dataframe_quick_analysis(_df))
    _how_methods = ['left', 'inner', 'right', 'outer']
    print(*["{}\n".format(_ele) for _ele in dataframe_merge(_df, _df2, _how_methods)])
