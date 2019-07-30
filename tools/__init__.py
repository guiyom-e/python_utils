# -*- coding: utf-8 -*-
# open source project
"""
Tools.
"""
import pdb

__id_filename__ = ".ID_tools-3DF36B5D-694A-4743-96A4-C02B269C95D5"  # must be before logger import

from tools.logger import logger  # import logger and set default working directory

# try to import required modules
_msg_ptrn = " ok"
test_lib = '[nothing tested yet]'
try:
    # numpy
    test_lib = 'numpy'
    import numpy

    logger.debug(_msg_ptrn.format(test_lib))

    # pandas
    test_lib = 'pandas'
    import pandas

    logger.debug(_msg_ptrn.format(test_lib))

    # matplotlib
    test_lib = 'matplotlib'
    import matplotlib

    logger.debug(_msg_ptrn.format(test_lib))
    test_lib = 'matplotlib.pyplot'
    import matplotlib.pyplot

    logger.debug(_msg_ptrn.format(test_lib))
    test_lib = 'matplotlib.patches'
    import matplotlib.patches

    logger.debug(_msg_ptrn.format(test_lib))

    # seaborn
    test_lib = 'seaborn'
    import seaborn

    logger.debug(_msg_ptrn.format(test_lib))

    # python-pptx
    test_lib = 'pptx'
    import pptx

    logger.debug(_msg_ptrn.format(test_lib))
    test_lib = 'all libraries ok'
except ImportError as err:
    logger.error("Error while trying to import Python modules! Failed to import '{}'.".format(test_lib))
    logger.error(err)
    if 'DLL load failed' in str(err):
        logger.error("Error may be linked to Anaconda distribution.\n"
                     "Try to use pip instead of conda to install modules or use a virtualenv")
    logger.exception(err)
    print("Opening Python debugger...")
    pdb.set_trace()

__version__ = '1.2.1'
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
