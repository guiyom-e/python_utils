# open source
import pandas as pd

from tools.logger import logger
from tools.helpers.models import Path
from tools.helpers.data_manager.file_utils import check_path_arguments
from tools.helpers.data_manager.filepath_manager import open_file, handle_permission_error


def _read_csv(path, **kwargs):
    try:
        df = pd.read_csv(path, **kwargs)
    except PermissionError as err:
        df = handle_permission_error(err, func=_read_csv, path=path, change_path_func=open_file)
    return df


def _read_excel(path, sheet_name=0, **kwargs):
    try:
        df = pd.read_excel(path, sheet_name=sheet_name, **kwargs)
    except PermissionError as err:
        kwargs.update({'sheet_name': sheet_name})
        df = handle_permission_error(err, func=_read_excel, path=path,
                                     kwargs=kwargs, change_path_func=open_file)
    return df


def read_data_file(path=None, config_dict=None, config_key=None, date_columns=None, sheet_name=0,
                   check_path=False, behaviour_on_error='error', open_file_kwargs=None, read_kwargs=None,
                   to_datetime_kwargs=None,):
    """Returns a dataframe with the content of the selected CSV or Excel file.

    :param path: file path. Must be CSV or Excel file (to be checked before with 'open_file' function).
    :param config_dict: dictionary-like object containing the configuration
    :param config_key: key of config_dict to get path (replaces path argument)
    :param date_columns: column or list of columns to format as datetime
    :param sheet_name: name or index of the Excel sheet (not used for CSV)
    :param check_path: if True, use open_file to check path
    :param behaviour_on_error: 'error' (default): raise an error, 'ignore': return None
    :param open_file_kwargs: kwargs for open_file function ONLY.
    :param read_kwargs: kwargs for read functions pd.read_excel ONLY.  # can evolve in the future
    :param to_datetime_kwargs: kwargs for pd.to_datetime function ONLY.
    :return:
    """
    path = check_path_arguments(path, config_dict, config_key)
    open_file_kwargs = open_file_kwargs or {}
    to_datetime_kwargs = to_datetime_kwargs or {}
    read_kwargs = read_kwargs or {}
    if check_path:
        open_file_kwargs['path'] = path if 'path' not in open_file_kwargs else open_file_kwargs['path']
        open_file_kwargs['title'] = "Open '{}' file".format(Path(path).filename) \
            if 'title' not in open_file_kwargs else open_file_kwargs['title']
        open_file_kwargs['filetype'] = 'data' if 'filetype' not in open_file_kwargs else open_file_kwargs['filetype']
        path = open_file(**open_file_kwargs)
    ext = path.ext
    if ext in ['.csv', '.txt']:
        df = _read_csv(path, **read_kwargs)
        logger.debug('File {} loaded in pandas dataframe.'.format(path))
        if date_columns:
            if isinstance(date_columns, str):
                date_columns = [date_columns]
            logger.debug('Converting {} columns to datetime type...'.format(len(date_columns)))
            for date_column in date_columns:
                df[date_column] = pd.to_datetime(df[date_column], **to_datetime_kwargs)
            logger.debug('Columns {} of file {} converted to datetime format.'.format(date_columns, path))
        if config_dict:  # save path in config dict
            config_dict[config_key] = path
        return df
    if ext.startswith('.xls'):
        df = _read_excel(path, sheet_name=sheet_name, **read_kwargs)
        logger.debug('File {} loaded in pandas dataframe.'.format(path))
        if config_dict:  # save path in config dict
            config_dict[config_key] = path
        return df
    logger.error('Invalid file extension {} for file {}'.format(ext, path))
    if behaviour_on_error == 'error':
        raise ValueError("No data loaded because path '{}' is invalid".format(path))
    logger.debug("None is returned.")
    return None
