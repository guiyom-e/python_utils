# open source
"""Utils to reload modules while python is launched."""
import importlib
import os
import types
from typing import Union, Callable

from tools.logger import logger


def reload_functions(module, functions: Union[list, tuple, Callable]):
    """Reloads a function or a list/tuple of functions."""
    if not isinstance(functions, (list, tuple)):
        functions = [functions]
    for func in functions:
        if isinstance(func, (list, tuple)):  # format  [(_, func1, _), (_, func2, _), ...]
            fn = func[1] if len(func) > 1 else None
        else:  # format [func1, func2, ...]
            fn = func
        if '__name__' in dir(fn):  # case of functions and classes
            name = fn.__name__
            if name == '<lambda>':
                continue
        elif isinstance(fn, str) and fn in dir(module):  # particular case of __all__ list
            name = fn
        else:
            logger.error("object '{}' not reloaded, wrong type or name.")
            return
        getattr(module, name)  # access to function seems sufficient to reload it.
        logger.debug("object '{}' reloaded".format(name))


def reload_package(package, reload_func=False, ls_func_names: Union[list, str] = '__all__'):
    """Reloads the module 'package' and the functions selected if 'reload_func' is True.

    :param package: package to reload (includes subpackages)
    :param reload_func: if True, reload selected functions (see ls_func_names arg)
    :param ls_func_names: name or list of names of iterables in __init__ which contains functions to reload.
    The iterable must have one of this format: [func1, func2, ...] or [(_, func1, _), (_, func2, _), ...]
    :return: None
    """
    if isinstance(ls_func_names, str):
        ls_func_names = [ls_func_names]
    assert (hasattr(package, "__package__"))
    fn = package.__file__
    fn_dir = os.path.dirname(fn) + os.sep
    module_visit = {fn}
    del fn

    def reload_recursive_ex(module):
        try:
            importlib.reload(module)
        except ImportError as err:
            logger.exception(err)
            logger.error("module '{}' could not be reloaded.".format(module))
            return
        if reload_func:
            for func_names in ls_func_names:
                if func_names in dir(module):
                    ls_functions = getattr(module, func_names)
                    reload_functions(module, ls_functions)
        logger.debug("module '{}' reloaded!".format(module.__name__))

        for module_child in vars(module).values():  # search subpackages in vars(module)
            if isinstance(module_child, types.ModuleType):  # if it is a module
                fn_child = getattr(module_child, "__file__", None)
                if (fn_child is not None) and fn_child.startswith(fn_dir):  # if it is a subpackage
                    if fn_child not in module_visit:  # if module has not benn reloaded yet
                        # print("reloading:", fn_child, "from", module)
                        module_visit.add(fn_child)
                        reload_recursive_ex(module_child)  # reload subpackages of this module

    return reload_recursive_ex(package)


def reload_modules(modules: Union[list, types.ModuleType], reload_func=False, ls_func_names='__all__'):
    """Reloads the modules in list 'modules' and the functions selected if 'reload_func' is True.

    Reload twice to be sure the majority of modules and dependencies are reloaded.
    It is possible that some modules with tricky dependencies are not completely reloaded
        for example:
        - if 'tools.helpers' depends on 'tools', the first reload is be sufficient to
        completely reload 'tools.helpers' as 'tools' is reloaded before 'tools.helpers'
        - if 'tools' depends on 'tools.helpers' (e.g. imports of 'tools.helpers' functions in __all__),
        the first reload is not sufficient to reload 'tools' as 'tools.helpers' is reloaded after 'tools'.
        Thus, a new reload is needed.
        - if 'tools' depends on 'tools.helpers' which depends on 'tools.helpers.utils', 'tools' can not
        be reloaded properly in one execution, so it is necessary to execute this function twice.
        Normally, this case is rare with modules with few submodules.

        To avoid uncompleted reloads, it is advised to pass a list of modules with few interdependence
        in the right order (lasts modules dependent of the first ones, not the contrary).

    :param modules: list of modules
    :param reload_func: if True, reload selected functions (see ls_func_names arg)
    :param ls_func_names: name or list of names of either:
        - an iterable (list or tuple) in __init__ which contains functions to reload (e.g. __all__).
          The iterable must have one of this format: [func1, func2, ...] or [(_, func1, _), (_, func2, _), ...]
        - a function in __init__
    :return: None
    """
    if not isinstance(modules, (list, set, tuple)):
        modules = [modules]
    for module in modules:
        reload_package(module, reload_func=False)
        reload_package(module, reload_func=reload_func, ls_func_names=ls_func_names)
    logger.info("modules reloaded")
