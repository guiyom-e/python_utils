import pdb

__id_filename__ = ".ID_tools-3DF36B5D-694A-4743-96A4-C02B269C95D5"  # must be before logger import

from tools.logger import logger  # import logger and set default working directory

# try to import required modules
_msg_ptrn = " ok"
test_module = '[nothing tested yet]'
try:
    # numpy
    test_module = 'numpy'
    import numpy

    logger.debug(_msg_ptrn.format(test_module))

    # pandas
    test_module = 'pandas'
    import pandas

    logger.debug(_msg_ptrn.format(test_module))

    # matplotlib
    test_module = 'matplotlib'
    import matplotlib

    logger.debug(_msg_ptrn.format(test_module))
    test_module = 'matplotlib.pyplot'
    import matplotlib.pyplot

    logger.debug(_msg_ptrn.format(test_module))
    test_module = 'matplotlib.patches'
    import matplotlib.patches

    logger.debug(_msg_ptrn.format(test_module))

    # seaborn
    test_module = 'seaborn'
    import seaborn

    logger.debug(_msg_ptrn.format(test_module))

    # python-pptx
    test_module = 'pptx'
    import pptx

    logger.debug(_msg_ptrn.format(test_module))
except ImportError as err:
    logger.error("Error while trying to import Python modules! Failed to import '{}'.".format(test_module))
    logger.error(err)
    if 'DLL load failed' in str(err):
        logger.error("Error may be linked to Anaconda distribution.\n"
                     "Try to use pip instead of conda to install modules or use a virtualenv")
    logger.exception(err)
    print("Opening Python debugger...")
    pdb.set_trace()

__version__ = '1.1.0'
__description__ = "Main tools"

__icon__ = '\n'

__help__ = r"""{} v {}
=======
 HELP!
=======
There is nothing here for the moment!
Edit __init__.py file in tools/ directory to add information.

{}

""".format(__description__, __version__, __icon__)
