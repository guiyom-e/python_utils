Troubleshooting - Possible errors and solutions
===============================================

Python not in PATH
------------------

Error
~~~~~

'python' not recognised as command

Solution
~~~~~~~~

Add Python to PATH: Edit system environment variables and add Python
directory to variable 'Path'
https://www.google.com/search?q=Add+Python+to+the+Windows+Path

Various import errors, with DLL load failures
---------------------------------------------

Imports of numpy, matplotlib.pyplot or seaborn fail with an Anaconda
distribution.

Possible errors
~~~~~~~~~~~~~~~

``AttributeError: type object 'Series' has no attribute 'to_list'``

``ImportError: DLL load failed: The specified procedure could not be found.``

Solution
~~~~~~~~

Open Anaconda Prompt and run the following lines:

``conda uninstall numpy llvmlite``

``pip install -r req_pip_1``

where ``req_pip_1`` is a requirement file with the packages uninstalled
with conda (with some exceptions).

No pptx module
--------------

Error
~~~~~

``ModuleNotFoundError: No module named 'pptx'``

Solution
~~~~~~~~

[With Anaconda distributions]

First, open Anaconda Prompt and uninstall lxml and Pillow packages (You
will also lose anaconda-navigator!): ``conda uninstall lxml Pillow``

Then, install ``python-pptx`` package: ``pip install python-pptx``

[Other distributions]

Install ``python-pptx`` package: ``pip install python-pptx``

If it doesn't work
~~~~~~~~~~~~~~~~~~

-  reinstall missing packages deleted during conda uninstallations
-  can use flag --force-reinstall if doesn't work

 .. warning::

    These methods may make Anaconda distribution unstable. Prefer
    installing Python with another distribution, such as WinPython!

Import errors
-------------

Possible errors
~~~~~~~~~~~~~~~

``ModuleNotFoundError: No module named 'tools'``

``ModuleNotFoundError: No module named 'general_scripts'``

Solution
~~~~~~~~

Scripts must be run from root directory (``python_utils/`` by default), not ``tools/`` or other
directory. Change the parameters of your IDE or run it from
``python_utils/`` using a main file. It is also possible to add
``python_utils/`` to python path by adding the following code at the
beginning of the executed script:

::

    import sys
    sys.path.insert(0, "C:/.../python_utils")  # absolute import
    # Or, if current working directory is `python_utils/tools`, for example:
    sys.path.insert(0, "..")  # relative import

Error with the compiled tool (.exe)
-----------------------------------

Possible errors
~~~~~~~~~~~~~~~

``ModuleNotFoundError: No module named 'distutils'``

Solution
~~~~~~~~

https://github.com/pyinstaller/pyinstaller/issues/4064

Add these lines at the beginning of the .spec file:

::

    import distutils
    if distutils.distutils_path.endswith('__init__.py'):
        distutils.distutils_path = os.path.dirname(distutils.distutils_path)

Don't forget to delete the folder ``build/main`` to recompile entirely
the file
