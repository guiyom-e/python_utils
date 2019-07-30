# -*- coding: utf-8 -*-
# open source project
"""
Functions to select and validate file or directory paths.
"""
import os
import stat
import datetime
import re
import shutil
import uuid
from typing import Union
import pdb

from tools.logger import logger
from tools.exceptions import UnknownError
from tools.helpers.utils import isiterable
from tools.helpers.models import Path, PathCollection
from tools.helpers.interface import messagebox
from tools.helpers.data_manager.file_utils import (FILETYPE_TO_FILEDIALOG_FILETYPES, choose_filedialog,
                                                   check_path_arguments, add_file_extension, check_extension)


# Select directory or file(s) to open
def _filedialog_open(path_type, **kwargs) -> Union[Path, PathCollection]:
    """Select the correct 'open' dialog whether the path type is a file or a directory."""
    if path_type == 'file':
        dialog_type = 'open'
    elif path_type == 'dir':
        dialog_type = 'open_dir'
    else:
        raise ValueError(path_type)
    kwargs.pop('dialog_type', None)
    return choose_filedialog(dialog_type=dialog_type, **kwargs)


# Select a directory
def open_dir(*args, **kwargs) -> Union[Path, PathCollection]:
    """Check path and open file dialog(s) to select directory(ies) if needed.

    >>> dir1 = os.path.dirname(__file__)
    >>> open_dir(dir1).filename
    Path: data_manager

    >>> open_dir(None, ask_path=False)
    Path: None

    >>> open_dir([dir1, dir1, None], multiple_paths=True, ask_path=False).filename
    [Path: data_manager, Path: data_manager, Path: ]
    """
    kwargs.pop('path_type', None)
    return open_file_or_dir(*args, path_type='dir', **kwargs)


def open_file(*args, **kwargs) -> Union[Path, PathCollection]:
    """Check path and open file dialog(s) to select file(s) if needed.

    >>> open_file(__file__).filename
    Path: filepath_manager.py

    >>> open_file(None, ask_path=False)
    Path: None

    >>> open_file([__file__, __file__, None], multiple_paths=True, ask_path=False).filename
    [Path: filepath_manager.py, Path: filepath_manager.py, Path: ]
    """
    kwargs.pop('path_type', None)
    return open_file_or_dir(*args, path_type='file', **kwargs)


# Select file(s)
def open_file_or_dir(path: Union[str, list, tuple, set] = None, config_dict=None, config_key=None,
                     multiple_paths=False, return_on_cancellation: str = None,
                     behavior_on_cancellation='warning', filetype=None, extension=None,
                     check_ext='ignore', ask_path=True, path_type='file', **kwargs) -> Union[Path, PathCollection]:
    """Check path and open file dialogs if needed.

    :param path: path to check. If path is None, a file dialog is opened to choose path, unless 'ask_path' is False
    :param config_dict: instead of path, use config_dict and config_key. path will be set to config_dict[config_key]
    :param config_key: instead of path, use config_dict and config_key. path will be set to config_dict[config_key]
    :param multiple_paths: if True, multiple files are allowed and returned as PathCollection (instead of Path)
    :param return_on_cancellation: return on user cancellation. Default: Path(None) (highly recommended)
    :param behavior_on_cancellation: error flag used to raise anomaly 'raise_no_file_selected_anomaly' on cancellation .
                                     Must be 'ask', 'ignore', 'warning', or 'error'.
    :param filetype: filetype in FILETYPE_TO_FILEDIALOG_FILETYPES keys. If filetype is None, extension is not checked.
    :param extension: final extension to check. If extension is None, extension is not checked.
    :param check_ext: error flag used to raise anomaly 'raise_bad_extension_anomaly'
    :param ask_path: if True and path is None, ask path to the user
    :param path_type: 'file' or 'dir'. 'file by default
    :param kwargs: keywords arguments for filedialog methods, such as 'title', 'message', 'filetypes', etc.
    :return: path or collection of paths
    """
    # Check of input arguments path_type, path, config_dict and config_key
    path = check_path_arguments(path, config_dict, config_key)
    if path_type not in {'file', 'dir', None}:
        msg = "path_type '{}' is not valid".format(path_type)
        logger.error(msg)
        raise ValueError(msg)
    is_path = 'isdir' if path_type == 'dir' else 'isfile'
    path_name = "directory" if path_type == 'dir' else "file"
    path_names = "directories" if path_type == 'dir' else "files"

    # If path is an iterable, explore it recursively.
    if isiterable(path) and multiple_paths:
        result = PathCollection()
        for r_path in path:
            result.append(open_file_or_dir(path=r_path,
                                           multiple_paths=False,
                                           return_on_cancellation=return_on_cancellation,
                                           behavior_on_cancellation=behavior_on_cancellation,
                                           filetype=filetype, extension=extension,
                                           check_ext=check_ext, ask_path=ask_path, path_type=path_type, **kwargs))
        return result

    # Invalid type for path.
    if path is not None and not isinstance(path, str):
        messagebox.showwarning(title='Python type error!',
                               message="Path passed to the function is of type '{}', not str.\n\n"
                                       "N.B.: to add multiple {}, 'multiple_paths' argument must be True.\n\n"
                                       "Path has to be set manually.".format(path_names, type(path)))
        path = None

    # Convert path to type Path
    path = Path(path)
    if path.isnone and not ask_path:  # If path and ask_path are both None, pass
        pass
    elif not getattr(path, is_path):  # If path is not a file/dir path (includes None path), open a file dialog.
        if not path.isnone:  # Shows a warning if wrong path (do not include None path)
            messagebox.showwarning(title='Error while trying to find the {}!'.format(path_name),
                                   message="The path '{}' doesn't correspond to any {}. "
                                           "Path has to be set manually.".format(path, path_name))
        if 'filetypes' not in kwargs and path_type == 'file':
            kwargs['filetypes'] = FILETYPE_TO_FILEDIALOG_FILETYPES[filetype]
        if 'title' not in kwargs:
            kwargs['title'] = "Open {}".format(path_names if multiple_paths else path_name) if path.isnone \
                else "Open '{}' {}".format(path.filename, path_name)

        path = _filedialog_open(path_type, multiple_paths=multiple_paths, return_on_cancellation=return_on_cancellation,
                                behavior_on_cancellation=behavior_on_cancellation, **kwargs)

    # Check extension
    if (isiterable(path) or not path.isnone) and path_type == 'file':
        chk_ext = check_extension(path, extension=extension, filetype=filetype, check_ext=check_ext)
        if not chk_ext:
            return open_file_or_dir(path=None,
                                    multiple_paths=multiple_paths,
                                    return_on_cancellation=return_on_cancellation,
                                    behavior_on_cancellation=behavior_on_cancellation,
                                    filetype=filetype, extension=extension,
                                    check_ext=check_ext, ask_path=ask_path, path_type=path_type, **kwargs)
    if config_dict:  # save the new path in config dict
        config_dict[config_key] = path
    return path


# Select file to save
def _filedialog_save(**kwargs) -> Path:
    """Select the correct 'save' dialog."""
    kwargs.pop('dialog_type', None)
    return choose_filedialog(dialog_type='save', **kwargs)


def _set_writable(path: str):
    """Make a file writable if it exists and is read-only."""
    if Path(path).isfile and not os.access(path, os.W_OK):
        try:
            os.chmod(path, stat.S_IWUSR | stat.S_IREAD)  # if read-only existing file, make it writable
        except PermissionError:
            logger.debug("Failed to change file properties of '{}'".format(path))
            return
        logger.debug("File '{}' is now writable.")


def _handle_existing_file_conflict(path: Path, overwrite='ask', backup=False, **kwargs) -> Union[Path, None]:
    """Handle conflict if a file already exist by opening adapted dialog."""
    # overwrite 'ask': ask user to modify overwrite arg into 'overwrite' (Yes) or 'rename' (No) or return None (Cancel)
    if overwrite == 'ask':
        logger.warning('User action needed!')
        res = messagebox.askyesnocancel(title="File existing",
                                        message="File {} already exists.\nDo you want to overwrite it?"
                                                "\n\nIf you select 'No', the file will be "
                                                "renamed automatically.".format(path))
        if res is None:
            logger.info("'Save file' operation cancelled by the user.".format(path))
            logger.debug("The path 'None' will be returned.")

            return None
        if res:
            overwrite = 'overwrite'
        else:
            overwrite = 'rename'

    # overwrite 'rename' or False: add '-i' at the end of the path to make it unique, where 'i' is an integer.
    if overwrite == 'rename' or overwrite is False:
        r_path, r_ext = path.splitext
        # def rename_method1(r_path, sep='-'):#todo
        ls_end = re.findall(r'-(\d+)$', r_path)
        if ls_end:  # if the path already ends by '-i', change end to 'i+1'
            end = ls_end[0]
            r_path = r_path[:-(len(end) + 1)]
            added_ending = "-{}".format(int(end) + 1)
        else:
            added_ending = "-1"
        n_path = r_path + added_ending + r_ext
        logger.debug("Path {} changed to {} (renaming)".format(path, n_path))
        return save_file(n_path, overwrite=overwrite, backup=backup, **kwargs)

    # backup True: backup the old file
    if backup and path.isfile:
        suffix = datetime.datetime.now().strftime("-%Y-%m-%d_%H-%M_") + uuid.uuid4().hex[:5]
        try:
            shutil.copyfile(path, path.radix + suffix + path.ext)
        except (PermissionError, FileNotFoundError) as err:
            logger.exception(err)
            logger.error("Failed to backup previous configuration file.")

    # overwrite 'overwrite' or True: do not modify the path and make the old file writable to allow overwriting
    if overwrite == 'overwrite' or overwrite is True:
        logger.debug("File {} will be overwritten".format(path))
        _set_writable(path)

    # overwrite 'ignore': do nothing
    elif overwrite == 'ignore':
        pass
    # other case of overwrite: do nothing (same as 'ignore')
    else:
        logger.warning("Unexpected argument 'overwrite'! File {} will be overwritten".format(path))
    return path


def save_file(path: Union[Path, str] = None, config_dict=None, config_key=None,
              return_on_cancellation=Path(None), behavior_on_cancellation='warning',
              auto_mkdir=True, extension=None, replace_ext=False, filetype=None,
              overwrite='ask', backup=False, **kwargs) -> Path:
    """Check the path to save a file.

    :param path: path or None
    :param config_dict: dictionary-like object containing the configuration
    :param config_key: key of config_dict to get path (replaces path argument)
   :param return_on_cancellation: return on user cancellation. Default: Path(None) (highly recommended)
    :param behavior_on_cancellation: error flag used to raise anomaly 'raise_no_file_selected_anomaly' on cancellation .
                                     Must be 'ask', 'ignore', 'warning', or 'error'.
    :param auto_mkdir: if True, try to create output directories if they don't exist
    :param filetype: filetype in FILETYPE_TO_FILEDIALOG_FILETYPES keys. If filetype is None, extension is not checked.
    :param extension: final extension to check. If extension is None, extension is not checked.
    :param replace_ext: if True, replaces extension instead of adding one
    :param overwrite: bool or flag 'ask', 'rename', 'ignore', 'overwrite', used in case file already exists
    :param backup: bool, used in case file already exists
    :param kwargs: for filedialog
    :return: path
    """
    # Check of input arguments.
    path = Path(check_path_arguments(path, config_dict, config_key))
    if 'filetypes' not in kwargs:
        kwargs.update({'filetypes': FILETYPE_TO_FILEDIALOG_FILETYPES[filetype]})
    # Ask for a path if path is None.
    if path.isnone:
        path = _filedialog_save(return_on_cancellation=return_on_cancellation,
                                behavior_on_cancellation=behavior_on_cancellation, **kwargs)

    # Check type of path.
    if not isinstance(path, str):
        messagebox.showwarning(title='Python type error!',
                               message="The path passed to the function is not a string."
                                       "Consider to take a look at the Python code! "
                                       "Path has to be set manually.")
        path = _filedialog_save(return_on_cancellation=return_on_cancellation,
                                behavior_on_cancellation=behavior_on_cancellation, **kwargs)

    # Check file directory
    file_dir = path.dirname
    if not file_dir.isdir and not path.isnone:
        if auto_mkdir:
            try:
                file_dir.makedir()
            except (FileNotFoundError, PermissionError) as err:
                logger.exception(err)
                messagebox.showwarning(title='Error while trying to create a directory!',
                                       message="The directory {} doesn't exist and can't be created. "
                                               "Please select another directory.".format(file_dir))
                path = _filedialog_save(return_on_cancellation=return_on_cancellation,
                                        behavior_on_cancellation=behavior_on_cancellation, **kwargs)
        else:
            messagebox.showwarning(title='Error while trying to access a directory!',
                                   message="The directory {} doesn't exist. "
                                           "Please select another directory.".format(file_dir))
            path = _filedialog_save(return_on_cancellation=return_on_cancellation,
                                    behavior_on_cancellation=behavior_on_cancellation, **kwargs)

    # Add extension
    n_path = add_file_extension(path, extension=extension, keep_existing=False, replace=replace_ext)

    # Check existing file
    if n_path.isfile:
        n_path = _handle_existing_file_conflict(n_path, overwrite=overwrite,
                                                return_on_cancellation=return_on_cancellation,
                                                behavior_on_cancellation=behavior_on_cancellation,
                                                auto_mkdir=auto_mkdir, extension=extension, backup=backup, **kwargs)
    if config_dict and n_path.isfile:  # save path in config dict
        config_dict[config_key] = n_path
    return n_path


#####################
# HANDLE EXCEPTIONS #
#####################

def handle_file_error(err, func, path, args=None, kwargs=None,
                      pos_path=0, key_path=None, change_path_func=save_file,
                      title='', msg='', return_if_ignore=None):
    """If PermissionError when opening/saving file, propose to retry, change file path or cancel

    :param err: exception
    :param func: function to execute if the user wants to retry
    :param path: file path
    :param args: args to pass to func
    :param kwargs: kwargs to pass to func
    :param pos_path: position of the positional argument path in func (only if key_path is None)
    :param key_path: name of the keyword argument path in func (if None, positional argument is used)
    :param change_path_func: function to get a new path, with no positional argument and 'initialdir' keyword argument
    :param title: title of the error
    :param msg: message of the error
    :param return_if_ignore: return if Ignore option is selected
    :return:
    """
    logger.debug(err)
    args = args or []
    kwargs = kwargs or {}
    title = title or 'File error!'
    msg = msg or "Unknown error with file '{}'. \nOriginal error: {}".format(path, err)
    logger.warning('User action needed!')
    res = messagebox.askcustomquestion(title=title, message=msg,
                                       choices=["Retry", "Rename automatically", "Change file path",
                                                "Ignore", "Debug (developer only)", "Cancel"])
    if res == "Retry":
        if key_path is not None:
            kwargs[key_path] = path
        else:
            args.insert(pos_path, path)
        return func(*args, **kwargs)
    if res == "Rename automatically":
        n_path = _handle_existing_file_conflict(path=path, overwrite='rename')
        if key_path is not None:
            kwargs[key_path] = n_path
        else:
            args.insert(pos_path, n_path)
        return func(*args, **kwargs)
    elif res == "Change file path":
        initialdir = Path(path).dirname if Path(path).dirname.exists else None
        if key_path is not None:
            kwargs[key_path] = change_path_func(initialdir=initialdir)
        else:
            args.insert(pos_path, change_path_func(initialdir=initialdir))
        return func(*args, **kwargs)
    elif res == "Ignore":
        logger.warning("Function ignored!")
        logger.debug("Function '{}' with path '{}' ignored!")
        return return_if_ignore
    elif res == "Debug (developer only)":
        pdb.set_trace()
    elif res in [None, "Cancel"]:
        err = UnknownError if not isinstance(err, BaseException) else err
        logger.exception(err)
        raise err.__class__(err)
    else:
        raise TypeError("Bad return of function 'messagebox.askcustomquestion': '{}'".format(res))


def handle_permission_error(err, func, path, args=None, kwargs=None,
                            pos_path=0, key_path=None, change_path_func=save_file,
                            title='', msg='', handle_read_only_error=False):
    """
    handle_read_only_error: True to handle the case of a read-only file: the function tries to make the file writable.
    """
    title = title or 'Permission error!'
    msg = msg or "Permission error for file '{}'. The file may be opened in another program\n" \
                 "or you don't have the rights to access to it. \nOriginal error: {}".format(path, err)
    if handle_read_only_error:
        _set_writable(path)
    return handle_file_error(err, func, path, args=args, kwargs=kwargs,
                             pos_path=pos_path, key_path=key_path, change_path_func=change_path_func,
                             title=title, msg=msg)


def handle_bad_extension_error(err, func, path, args=None, kwargs=None,
                               pos_path=0, key_path=None, change_path_func=save_file,
                               title='', msg='', extension=None):
    """
    extension: default extension to add to the path. If None, nothing is changed
    """
    title = title or 'Bad extension error!'
    msg = msg or "File '{}' has an unsupported extension '{}'. \nOriginal error: {}".format(path, Path(path).ext, err)
    path = Path(path).join_ext(extension)
    return handle_file_error(err, func, path, args=args, kwargs=kwargs,
                             pos_path=pos_path, key_path=key_path, change_path_func=change_path_func,
                             title=title, msg=msg)


def handle_file_not_found_error(err, func, path, args=None, kwargs=None,
                                pos_path=0, key_path=None, change_path_func=save_file,
                                title='', msg=''):
    title = title or 'File not found!'
    msg = msg or "File '{}' can not be found.\n" \
                 "Original error: {}".format(path, Path(path).ext, err)
    return handle_file_error(err, func, path, args=args, kwargs=kwargs,
                             pos_path=pos_path, key_path=key_path, change_path_func=change_path_func,
                             title=title, msg=msg)


# Testing purposes
if __name__ == '__main__':
    print(open_file())
    print(open_file(['a', 'b'], multiple_paths=False))

    # pdb.set_trace()
    print(open_file('a.b', extension="txt", check_ext='retry'))
    # print(save_file())
