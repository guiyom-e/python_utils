# -*- coding: utf-8 -*-
# open source project
"""
Utils linked to files.
"""
import datetime
import os
from typing import Union, Dict

from tools.logger import logger
from tools.helpers.interface.anomalies import raise_no_file_selected_anomaly, raise_bad_extension_anomaly
from tools.helpers import isinstance_filetypes, isiterable
from tools.helpers.interface import filedialog
from tools.helpers.models import Path, FileExt, DefaultFiletypesDict

FILETYPE_TO_FILEDIALOG_FILETYPES = DefaultFiletypesDict({
    'excel': [('Excel workbook', '*.xlsx *.xls'), ('all_files', '*.*')],
    'csv': [('CSV file', '*.csv'), ('all_files', '*.*')],
    'data': [('Excel workbook', '*.xlsx'), ('CSV file', '*.csv'), ('all_files', '*.*')]
})
FILETYPE_TO_EXTENSION = {'excel': FileExt(".xlsx"),
                         "csv": FileExt(".csv"),
                         }


def check_path_arguments(path: Union[Path, str], config_dict: Dict,
                         config_key: str) -> Union[Path, str]:
    """User should use either 'path' or 'config_dict' and 'config_key' arguments to indicate a path."""
    if (path and (config_dict or config_key)) or (bool(config_dict) != bool(config_key)):
        msg = "Arguments must be 'path' or 'config_dict' and 'config_key'."
        logger.error(msg)
        raise TypeError(msg)
    if config_dict:
        path = config_dict.get(config_key, None)
    return path


def choose_filedialog(dialog_type: str, multiple_paths: bool = False, return_on_cancellation: str = None,
                      behavior_on_cancellation: str = 'ignore', initialdir: str = None, filetypes: list = None,
                      title: str = None, **kwargs) -> Union[tuple, Path]:
    """Open a filedialog window."""
    # Check dialog type.
    if dialog_type == 'save':
        user_input_func = filedialog.asksaveasfilename
    elif dialog_type == 'open':
        if multiple_paths:  # selection of multiple files
            user_input_func = filedialog.askopenfilenames
        else:  # selection of a unique file
            user_input_func = filedialog.askopenfilename
    elif dialog_type == 'open_dir':
        user_input_func = filedialog.askdirectory
    else:
        msg = "Argument 'dialog_type' must be 'save, 'open' or 'open_dir'."
        logger.error(msg)
        raise ValueError(msg)

    # Check inputs.
    if filetypes is None or not isinstance_filetypes(filetypes):
        filetypes = [("all files", "*.*")]
    if not isinstance(initialdir, str) or not Path(initialdir).isdir:
        initialdir = None
    if not isinstance(title, str):
        title = None

    # Get filenames.
    logger.warning('User action needed!')
    filetypes_kwargs = {} if dialog_type == 'open_dir' else dict(filetypes=filetypes)
    path = user_input_func(title=title, initialdir=initialdir, **filetypes_kwargs)
    if not path:  # if no file selected
        # raise an anomaly with flag behavior_on_cancellation ('ask', 'ignore', 'warning' or 'error').
        raise_no_file_selected_anomaly(flag=behavior_on_cancellation)
        return Path(return_on_cancellation)
    return Path(path)


def add_file_extension(path: Union[str, Path], extension=None,
                       replace=False, keep_existing=False, force_add=False) -> Path:
    """Add a specific extension to 'path'.

    :param path: path
    :param extension: extension. None is considered as '' extension
    :param replace: replace instead of append extension
    :param keep_existing: add extension only if it doesn't already exist
    :param force_add: add extension even if the correct extension already exists (not recommended)
    :return Path object
    """
    path = Path(path)
    if path.ext and keep_existing:
        if path.ext != FileExt(extension):
            logger.warning("Bad extension kept: {}".format(path.ext))
        return path
    if replace:
        return path.replace_ext(extension)
    if path.ext == FileExt(extension) and not force_add:
        return path
    return path.join_ext(extension)


def check_extension(path: Union[Path, list, tuple, set], extension=None,
                    filetype=None, check_ext='ignore') -> bool:
    """Check extension of path or collection of paths which must arg 'extension' or
    extension linked to 'filetype', unless they are None"""
    if isiterable(path):
        for ele in path:
            chk_ext = check_extension(ele, extension=extension, filetype=filetype,
                                      check_ext=check_ext)
            if chk_ext is False:
                return False
        return True
    ext1 = FILETYPE_TO_EXTENSION.get(filetype, None)
    ext2 = FileExt(extension) if extension is not None else None
    file_ext = path.ext
    # Path extension must match 'extension' and/or 'filetype' (or not considered).
    if (file_ext == ext1) or (file_ext == ext2) or (ext1 is None and ext2 is None):
        return True
    expected_ext = " or ".join([ext for ext in [ext1, ext2] if ext])
    msg = "The selected file has a bad extension '{}'. Expected '{}'.".format(file_ext, expected_ext)
    if check_ext == 'retry':
        msg += "\n\nPlease try again."
        raise_bad_extension_anomaly(flag='warning', msg=msg)
        return False
    raise_bad_extension_anomaly(flag=check_ext, msg=msg)
    return True


def get_path_metadata(path, metadata_dict=None):
    """Returns a dictionary with path information:
    'path', 'abspath' and 'exists' in all cases;
    'isabs' (os.path.isabs), 'type' (one of 'dir', 'file', 'link', 'unknown'),
    'creation_date', 'access_date', 'modification_date', 'size' (in bytes),
    'readable', 'writable' and 'executable' attributes
    if the path exists.

    If metadata_dict argument exists and is a dictionary, modify it in place."""
    metadata_dict = metadata_dict if isinstance(metadata_dict, dict) else {}
    if os.path.isdir(path):
        type_path = 'dir'
    elif os.path.isfile(path):
        type_path = 'file'
    elif os.path.islink(path):
        type_path = 'link'
    else:
        type_path = 'unknown'
    if os.path.exists(path):  # equivalent to Path(path).exists
        metadata_dict.update({
            'path': path,
            'abspath': os.path.abspath(path),
            'exists': True,
            'isabs': os.path.isabs(path),
            'type': type_path,
            'creation_date': datetime.datetime.fromtimestamp(os.path.getctime(path)),  # datetime type
            'access_date': datetime.datetime.fromtimestamp(os.path.getatime(path)),  # datetime type
            'modification_date': datetime.datetime.fromtimestamp(os.path.getmtime(path)),  # datetime type
            'size': os.path.getsize(path),  # size in bytes
            'readable': os.access(path, os.R_OK),
            'writable': os.access(path, os.W_OK),
            'executable': os.access(path, os.X_OK),
        })
    else:
        metadata_dict.update({
            'path': path,
            'abspath': os.path.abspath(path),
            'exists': False,
        })
    return metadata_dict
