Basic installation
==================

1. Install python 3.5+ (Python 3.7+ recommended in 1.4+ version)

 * For Windows, it is possible to install WinPython for example : https://winpython.github.io/
 * For Linux distributions based on Debian, ``sudo apt-get install python3`` should work as well.

2. Preferably install a virtual environment in ``venv/``

 * Open a terminal (cmd in Windows)
 * Type ``pip install virtualenv`` or ``python3 -m pip install virtualenv`` (Linux) / ``python -m pip install virtualenv`` (Windows)
 * Type ``virtualenv venv`` (precise the version of python to use if needed)

3. Install requirements in the virtual environment:

 * ``tools/venv/Scripts/activate.bat`` (Windows)  or
   ``source tools/venv/bin/activate`` (Linux)

 * ``pip install -r requirements.txt``

4. You're done!

Setup of executable version
===========================
To compile ``main.py`` into ``main.exe`` file, run ``setup.bat`` (root directory) and select the first option ``1``.

Update documentation
====================
Windows
-------
To update auto-generated documentation, run ``setup.bat`` (root directory) and select the seventh option ``7``.

Linux
-----
To update auto-generated documentation, use ``docs/.config/Makefile``:

::

    cd docs/.config/
    make html

.. note::

    To re-generate Python packages documentation,
    when a new module is created for example, delete the unwanted files in ``docs/.config/sources``
    and run the following commands:
    ::
        cd docs/.config/
        sphinx-apidoc -o source ../../

.. note:: To update github documentation with gh-pages, first configure a repo ``python_utils_docs`` next to
          ``python_utils`` (see https://daler.github.io/sphinxdoc-test/includeme.html ),
          then use ``make update-gh-pages``.

Project tree
============

The main idea of the project tree is to reduce the number of items in the root directory (still from 11 to 17 items)
in order to allow non-developers to use tools without being concerned by configuration, logs, etc.
That's why ``config/``, ``logs/``, ``tests/`` are in ``tools/`` directory and that makefiles or setup scripts are
in ``docs/`` or ``build/``.

::

    python_utils
    |-- build                       <== directory for Windows builds
    |   |-- main.spec               <-- specification to compile executable version with pyinstaller
    |   `-- inno_setup_script.iss   <-- Inno Setup script to create a setup
    |
    |-- data                        <== data files
    |   `-- data files              <<< your own data
    |
    |-- docs                        <== documentation files
    |   |-- .config/                <-- sphinx configuration and sources + other documentation scripts
    |   |   |-- conf.py             <-- sphinx configuration
    |   |   |-- index.rst           <-- sphinx index
    |   |   |-- Makefile            <-- makefile (Linux) to generate developer documentation
    |   |   |-- Makefile.ps1        <-- powershell script to convert Word documents to PDF
    |   |   `-- source/             <-- rst documentation sources
    |   |-- troubleshooting/        <-- documentation to debug errors
    |   |-- developer_doc/          <-- auto-generated developer documentation
    |   `-- other documents         <<< your own documents
    |
    |-- scripts/                    <== scripts and modules
    |   |-- sample.py               <-- template script
    |   `-- scripts or modules      <<< your own scripts and modules
    |
    |-- tools/                      <== packages and modules (utils)
    |   |-- config/                 <-- configuration files INI
    |   |-- helpers/                <-- functions
    |   |   |-- advanced_utils/     <-- date and dataframe utils
    |   |   |-- config_manager/     <-- configuration manager
    |   |   |-- data_manager/       <-- file and dataframe manager
    |   |   |-- interface/          <-- user interfaces and enhanced messagebox / simpledialog
    |   |   |-- models/             <-- model classes
    |   |   |-- utils/              <-- simple utils
    |   |   |-- other packages      <<< your own utils
    |   |   `-- __init__.py
    |   |-- logs/                   <-- directory to save logs
    |   |-- tests/                  <-- test directory
    |   |-- __init__.py
    |   |-- exceptions.py
    |   |-- favicon.ico
    |   `-- logger.py
    |
    |-- other project               <<< your own project (instead of using scripts/)
    |
    |-- .gitignore
    |-- main.bat                    <-- launches main.py
    |-- main.py                     <-- main python file
    |-- README.md                   <-- readme (markdown, overview)
    |-- README.rst                  <-- readme (ReST, installation process)
    |-- requirements.txt            <-- python requirements
    `-- setup.bat                   <-- script to create an executable version (Windows)
