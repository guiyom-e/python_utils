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

Fail to install psycopg2
------------------------

Error
~~~~~

``Command "python setup.py egg_info" failed with error code 1 in /tmp/pip-install-s47hdlx4/psycopg2/``

Solution
~~~~~~~~
See https://www.psycopg.org/docs/install.html on error


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

Previous version not installed (.exe)
-------------------------------------

It is normal that logs and configuration files are not deleted by the uninstall setup.

A real issue can appear if you moved your installation directory and you then try uninstall 
with the uninstall setup or withe the new setup. The setup uninstall the program but either don't delete
program files or don't find the uninstaller (if uninstallation with a new setup) so don't uninstall 
properly the previous version.

In these cases, save your files, run the unistaller (to delete registry keys) and delete the remaining directory.

Error with the compiled tool (.exe)
-----------------------------------

Error detected
WARNING: file already exists but should not: C:\Users\USER~1\AppData\Local\Temp\_MEIXXXXXX\xxx
where x can be replaced by the actual paths and USER~1 is your personal directory.

Solution
~~~~~~~~

This bug can be linked to temporary files created by previous versions.

Ignore all these errors.
Quit the program.
Delete ``C:\Users\USER~1\AppData\Local\Temp\_MEIXXXXXX`` directory.
Delete all directories and files in ``C:\Users\USER~1\AppData\Local\Temp\`` that are present
in the root of the Python project.
In case of doubt, it is also possible to delete temporary files using recommended cleaning tools and reboot.

