# open source
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


def open_dir(**kwargs) -> Path:
    return choose_filedialog(dialog_type='open_dir', **kwargs)


def _filedialog_open(**kwargs) -> Union[Path, PathCollection]:
    return choose_filedialog(dialog_type='open', **kwargs)


def open_file(path: Union[str, Path, list, tuple, set] = None, config_dict=None, config_key=None,
              multiple_files=False, return_on_cancellation=Path(None),
              behavior_on_cancellation='warning', filetype=None, extension=None,
              check_ext='ignore', ask_path=True, **kwargs) -> Union[Path, PathCollection]:
    """Check path and open file dialogs if needed.

    :param path: path to check. If path is None, a file dialog is opened to choose path, unless 'ask_path' is False
    :param config_dict: instead of path, use config_dict and config_key. path will be set to config_dict[config_key]
    :param config_key: instead of path, use config_dict and config_key. path will be set to config_dict[config_key]
    :param multiple_files: if True, multiple files are allowed and returned as PathCollection (instead of Path)
    :param return_on_cancellation: return on user cancellation. Default: Path(None) (highly recommended)
    :param behavior_on_cancellation: error flag used to raise anomaly 'raise_no_file_selected_anomaly' on cancellation .
                                     Must be 'ask', 'ignore', 'warning', or 'error'.
    :param filetype: filetype in FILETYPE_TO_FILEDIALOG_FILETYPES keys. If filetype is None, extension is not checked.
    :param extension: final extension to check. If extension is None, extension is not checked.
    :param check_ext: error flag used to raise anomaly 'raise_bad_extension_anomaly'
    :param ask_path: if True and path is None, ask path to the user
    :param kwargs: keywords arguments for filedialog methods, such as 'title', 'message', 'filetypes', etc.
    :return: path or collection of paths
    """
    # Check of input arguments and conversion to Path type.
    path = check_path_arguments(path, config_dict, config_key)

    # If path is an iterable, explore it recursively.
    if isiterable(path) and multiple_files:
        result = PathCollection()
        for r_path in path:
            result.append(open_file(path=r_path,
                                    multiple_files=False,
                                    return_on_cancellation=return_on_cancellation,
                                    behavior_on_cancellation=behavior_on_cancellation,
                                    filetype=filetype, extension=extension,
                                    check_ext='ignore', **kwargs))
        return result

    # Invalid type for path.
    if path is not None and not isinstance(path, str):
        messagebox.showwarning(title='Python type error!',
                               message="Path passed to the function is of type '{}', not str.\n"
                                       "N.B.: to add multiple files, 'multiple_files' argument must be True.\n\n"
                                       "Path has to be set manually.".format(type(path)))
        path = None

    path = Path(path)  # Convert path to type Path
    if path.isnone and not ask_path:
        pass
    elif not path.isfile:  # If path is not a file path (includes None path), open filedialog.
        if not path.isnone:  # Shows a warning if wrong path (do not include None path)
            messagebox.showwarning(title='Error while trying to find the file!',
                                   message="The path '{}' doesn't correspond to any file. "
                                           "Path has to be set manually.".format(path))
        if 'filetypes' not in kwargs:
            kwargs['filetypes'] = FILETYPE_TO_FILEDIALOG_FILETYPES[filetype]
        if 'title' not in kwargs:
            kwargs['title'] = "Open file(s)" if path.isnone else "Open '{}' file(s)".format(path.filename)
        path = _filedialog_open(multiple_files=multiple_files, return_on_cancellation=return_on_cancellation,
                                behavior_on_cancellation=behavior_on_cancellation, **kwargs) or Path(None)

    if isiterable(path) or not path.isnone:  # TODO: return_on_cancellation should be Path(None)
        chk_ext = check_extension(path, extension=extension, filetype=filetype, check_ext=check_ext)
        if not chk_ext:
            return open_file(path=None,
                             multiple_files=multiple_files,
                             return_on_cancellation=return_on_cancellation,
                             behavior_on_cancellation=behavior_on_cancellation,
                             filetype=filetype, extension=extension,
                             check_ext=check_ext, **kwargs)
    if config_dict:  # save path in config dict
        config_dict[config_key] = path
    return path


def _filedialog_save(**kwargs) -> Path:
    return choose_filedialog(dialog_type='save', **kwargs)


def _set_writable(path):
    if Path(path).isfile and not os.access(path, os.W_OK):
        try:
            os.chmod(path, stat.S_IWUSR | stat.S_IREAD)  # if read-only existing file, make it writable
        except PermissionError:
            logger.debug("Failed to change file properties of '{}'".format(path))
            return
        logger.debug("File '{}' is now writable.")


def _handle_existing_file_conflict(path: Path, overwrite='ask', backup=False, **kwargs) -> Union[Path, None]:
    if overwrite == 'ask':
        logger.warning('User action needed!')
        res = messagebox.askyesnocancel(title="File existing",
                                        message="File {} already exists. Do you want to overwrite it?"
                                                "If you select 'No', the file will be "
                                                "renamed automatically.".format(path))
        if res is None:
            logger.info("'Save file' operation cancelled by the user.".format(path))
            logger.debug("The path 'None' will be returned.")

            return None
        if res:
            overwrite = 'overwrite'
        else:
            overwrite = 'rename'
    if overwrite == 'rename' or overwrite is False:
        r_path, r_ext = path.splitext
        # def rename_method1(r_path, sep='-'):#todo
        ls_end = re.findall(r'-(\d+)$', r_path)
        if ls_end:
            end = ls_end[0]
            r_path = r_path[:-(len(end) + 1)]
            added_ending = "-{}".format(int(end) + 1)
        else:
            added_ending = "-1"
        n_path = r_path + added_ending + r_ext
        logger.debug("Path {} changed to {} (renaming)".format(path, n_path))
        return save_file(n_path, overwrite=overwrite, backup=backup, **kwargs)

    if backup and path.isfile:
        suffix = datetime.datetime.now().strftime("-%Y-%m-%d_%H-%M_") + uuid.uuid4().hex[:5]
        try:
            shutil.copyfile(path, "{}{}.{}".format(path.radix, suffix, path.ext))
        except (PermissionError, FileNotFoundError) as err:
            logger.exception(err)
            logger.error("Failed to backup previous configuration file.")
    if overwrite == 'overwrite' or overwrite is True:
        logger.debug("File {} will be overwritten".format(path))
        _set_writable(path)
    elif overwrite == 'ignore':
        pass
    else:
        logger.warning("Unexpected argument 'overwrite'! File {} will be overwritten".format(path))
    return path


def save_file(path: Union[Path, str] = None, config_dict=None, config_key=None,
              return_on_cancellation=Path(None), behavior_on_cancellation='warning',
              auto_mkdir=True, extension=None, replace_ext=False, filetype=None, check_ext='ignore',  # TODO
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
    :param check_ext: error flag used to raise anomaly 'raise_bad_extension_anomaly'
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
    if not file_dir.isdir:
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
                                       answers=["Retry", "Rename automatically", "Change file path",
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
        return None
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
    print(open_file(['a', 'b'], multiple_files=False))

    # pdb.set_trace()
    print(open_file('a.b', extension="txt", check_ext='retry'))
    # print(save_file())
