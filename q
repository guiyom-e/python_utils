* [33mcommit eb7d5ea06f9cd20cd5d60dbec0eba6743f2e38fe[m[33m ([m[1;36mHEAD -> [m[1;32mgh-pages[m[33m, [m[1;31morigin/gh-pages[m[33m)[m
[31m|[m Author: guiyom <guiyom@PC2>
[31m|[m Date:   Sun Aug 11 14:06:17 2019 +0800
[31m|[m 
[31m|[m     added .nojekyll
[31m|[m 
[31m|[m  .nojekyll | 0
[31m|[m  1 file changed, 0 insertions(+), 0 deletions(-)
[31m|[m 
* [33mcommit 1865ce719a34e31f1957c99d43eea0946c442a2f[m
[31m|[m Author: guiyom <guiyom@PC2>
[31m|[m Date:   Sun Aug 11 13:58:08 2019 +0800
[31m|[m 
[31m|[m     [doc] docs v1.3 built
[31m|[m 
[31m|[m  .buildinfo                                   |     4 [32m+[m
[31m|[m  .gitignore                                   |    15 [31m-[m
[31m|[m  README.md                                    |    27 [31m-[m
[31m|[m  index.rst => _sources/index.rst.txt          |    13 [32m+[m[31m-[m
[31m|[m  _sources/source/includeme.rst.txt            |     1 [32m+[m
[31m|[m  _sources/source/main.rst.txt                 |     7 [32m+[m
[31m|[m  _sources/source/modules.rst.txt              |     9 [32m+[m
[31m|[m  _sources/source/scripts.rst.txt              |    22 [32m+[m
[31m|[m  .../tools.helpers.advanced_utils.rst.txt     |    38 [32m+[m
[31m|[m  .../tools.helpers.config_manager.rst.txt     |    46 [32m+[m
[31m|[m  .../tools.helpers.data_manager.rst.txt       |    54 [32m+[m
[31m|[m  .../source/tools.helpers.interface.rst.txt   |   102 [32m+[m
[31m|[m  _sources/source/tools.helpers.models.rst.txt |    54 [32m+[m
[31m|[m  _sources/source/tools.helpers.rst.txt        |    22 [32m+[m
[31m|[m  _sources/source/tools.helpers.utils.rst.txt  |    38 [32m+[m
[31m|[m  _sources/source/tools.rst.txt                |    38 [32m+[m
[31m|[m  _sources/source/tools.tests.rst.txt          |    10 [32m+[m
[31m|[m  _static/basic.css                            |   763 [32m++[m
[31m|[m  _static/classic.css                          |   261 [32m+[m
[31m|[m  _static/default.css                          |     1 [32m+[m
[31m|[m  _static/doctools.js                          |   314 [32m+[m
[31m|[m  _static/documentation_options.js             |    10 [32m+[m
[31m|[m  _static/file.png                             |   Bin [31m0[m -> [32m286[m bytes
[31m|[m  _static/jquery-3.2.1.js                      | 10253 [32m+++++++++++++++[m
[31m|[m  _static/jquery.js                            |     4 [32m+[m
[31m|[m  _static/language_data.js                     |   297 [32m+[m
[31m|[m  _static/minus.png                            |   Bin [31m0[m -> [32m90[m bytes
[31m|[m  _static/plus.png                             |   Bin [31m0[m -> [32m90[m bytes
[31m|[m  _static/pygments.css                         |    69 [32m+[m
[31m|[m  _static/searchtools.js                       |   506 [32m+[m
[31m|[m  _static/sidebar.js                           |   159 [32m+[m
[31m|[m  _static/underscore-1.3.1.js                  |   999 [32m++[m
[31m|[m  _static/underscore.js                        |    31 [32m+[m
[31m|[m  build/inno_setup_script.iss                  |   128 [31m-[m
[31m|[m  conf.py                                      |    55 [31m-[m
[31m|[m  data/.keep                                   |     1 [31m-[m
[31m|[m  docs/.keep                                   |     1 [31m-[m
[31m|[m  docs/_config.yml                             |     1 [31m-[m
[31m|[m  genindex.html                                |  1381 [32m++[m
[31m|[m  index.html                                   |   155 [32m+[m
[31m|[m  main.bat                                     |     4 [31m-[m
[31m|[m  main.py                                      |   102 [31m-[m
[31m|[m  main.spec                                    |    37 [31m-[m
[31m|[m  objects.inv                                  |   Bin [31m0[m -> [32m3497[m bytes
[31m|[m  py-modindex.html                             |   326 [32m+[m
[31m|[m  requirements.txt                             |   110 [31m-[m
[31m|[m  scripts/__init__.py                          |     6 [31m-[m
[31m|[m  scripts/sample.py                            |    28 [31m-[m
[31m|[m  search.html                                  |    93 [32m+[m
[31m|[m  searchindex.js                               |     1 [32m+[m
[31m|[m  setup.bat                                    |   137 [31m-[m
[31m|[m  source/includeme.html                        |   145 [32m+[m
[31m|[m  source/main.html                             |   139 [32m+[m
[31m|[m  source/modules.html                          |   136 [32m+[m
[31m|[m  source/scripts.html                          |   133 [32m+[m
[31m|[m  source/tools.helpers.advanced_utils.html     |   757 [32m++[m
[31m|[m  source/tools.helpers.config_manager.html     |   566 [32m+[m
[31m|[m  source/tools.helpers.data_manager.html       |   620 [32m+[m
[31m|[m  source/tools.helpers.html                    |   221 [32m+[m
[31m|[m  source/tools.helpers.interface.html          |  1563 [32m+++[m
[31m|[m  source/tools.helpers.models.html             |   635 [32m+[m
[31m|[m  source/tools.helpers.utils.html              |   598 [32m+[m
[31m|[m  source/tools.html                            |   239 [32m+[m
[31m|[m  source/tools.tests.html                      |   122 [32m+[m
[31m|[m  ...ools-3DF36B5D-694A-4743-96A4-C02B269C95D5 |     1 [31m-[m
[31m|[m  tools/__init__.py                            |    78 [31m-[m
[31m|[m  tools/config/config.ini.default              |     2 [31m-[m
[31m|[m  tools/exceptions.py                          |    20 [31m-[m
[31m|[m  tools/favicon.ico                            |   Bin [31m443487[m -> [32m0[m bytes
[31m|[m  tools/helpers/__init__.py                    |    12 [31m-[m
[31m|[m  tools/helpers/advanced_utils/__init__.py     |    21 [31m-[m
[31m|[m  .../advanced_utils/dataframe_utils.py        |    97 [31m-[m
[31m|[m  tools/helpers/advanced_utils/date_utils.py   |   465 [31m-[m
[31m|[m  tools/helpers/config_manager/__init__.py     |    74 [31m-[m
[31m|[m  .../config_manager/config_conversion.py      |   343 [31m-[m
[31m|[m  tools/helpers/config_manager/config_dict.py  |   591 [31m-[m
[31m|[m  .../helpers/config_manager/config_models.py  |   610 [31m-[m
[31m|[m  tools/helpers/data_manager/__init__.py       |    42 [31m-[m
[31m|[m  tools/helpers/data_manager/data_loader.py    |   102 [31m-[m
[31m|[m  tools/helpers/data_manager/data_writer.py    |   113 [31m-[m
[31m|[m  tools/helpers/data_manager/file_utils.py     |   121 [31m-[m
[31m|[m  .../helpers/data_manager/filepath_manager.py |   417 [31m-[m
[31m|[m  tools/helpers/data_manager/plots.py          |    28 [31m-[m
[31m|[m  tools/helpers/interface/__init__.py          |    64 [31m-[m
[31m|[m  tools/helpers/interface/advanced_wrappers.py |    75 [31m-[m
[31m|[m  tools/helpers/interface/anomalies.py         |   136 [31m-[m
[31m|[m  tools/helpers/interface/basics.py            |    58 [31m-[m
[31m|[m  tools/helpers/interface/custom_dialog.py     |   379 [31m-[m
[31m|[m  tools/helpers/interface/custom_messagebox.py |   136 [31m-[m
[31m|[m  tools/helpers/interface/date_picker.py       |   742 [31m--[m
[31m|[m  tools/helpers/interface/logger_widget.py     |    64 [31m-[m
[31m|[m  tools/helpers/interface/main_interface.py    |   208 [31m-[m
[31m|[m  tools/helpers/interface/text_frame.py        |    59 [31m-[m
[31m|[m  tools/helpers/interface/tooltip.py           |    59 [31m-[m
[31m|[m  tools/helpers/interface/wrappers.py          |   327 [31m-[m
[31m|[m  tools/helpers/models/__init__.py             |    25 [31m-[m
[31m|[m  tools/helpers/models/dict_models.py          |   108 [31m-[m
[31m|[m  tools/helpers/models/metaclasses.py          |    58 [31m-[m
[31m|[m  tools/helpers/models/path_models.py          |   253 [31m-[m
[31m|[m  tools/helpers/models/str_models.py           |   331 [31m-[m
[31m|[m  tools/helpers/models/types_models.py         |   159 [31m-[m
[31m|[m  tools/helpers/utils/__init__.py              |    22 [31m-[m
[31m|[m  tools/helpers/utils/decorators.py            |    73 [31m-[m
[31m|[m  tools/helpers/utils/module_utils.py          |   111 [31m-[m
[31m|[m  tools/helpers/utils/utils.py                 |   188 [31m-[m
[31m|[m  tools/logger.py                              |   112 [31m-[m
[31m|[m  tools/logs/.keep                             |     1 [31m-[m
[31m|[m  tools/src/.keep                              |     1 [31m-[m
[31m|[m  tools/src/readme.txt                         |     1 [31m-[m
[31m|[m  tools/tests/__init__.py                      |     5 [31m-[m
[31m|[m  tools/troubleshooting/req_pip_1              |    25 [31m-[m
[31m|[m  tools/troubleshooting/requirements.txt       |    90 [31m-[m
[31m|[m  tools/troubleshooting/troubleshooting.md     |    87 [31m-[m
[31m|[m  tools/troubleshooting/uninstall_conda_1      |    26 [31m-[m
[31m|[m  114 files changed, 21951 insertions(+), 7776 deletions(-)
[31m|[m 
* [33mcommit 2716c8607c42d4fbd6830ffd6aecad1ea6b3e0d4[m[33m ([m[1;31morigin/master[m[33m, [m[1;31morigin/HEAD[m[33m, [m[1;32mmaster[m[33m)[m
[31m|[m Author: guiyom <guiyom@PC2>
[31m|[m Date:   Fri Aug 9 23:56:34 2019 +0800
[31m|[m 
[31m|[m     [repo] moved /tools/venv to /venv + updated .gitignore and requirements
[31m|[m     
[31m|[m     * v 1.3: favicon changed
[31m|[m     * setup with variables for file paths and app name
[31m|[m 
[31m|[m  .gitignore        |   5 [32m+++[m[31m--[m
[31m|[m  main.bat          |   8 [32m++++[m[31m----[m
[31m|[m  main.spec         |   2 [32m+[m[31m-[m
[31m|[m  requirements.txt  |  25 [32m++++++++++++++++++[m[31m-------[m
[31m|[m  setup.bat         |  23 [32m++++++++++++++++[m[31m-------[m
[31m|[m  tools/__init__.py |   2 [32m+[m[31m-[m
[31m|[m  tools/favicon.ico | Bin [31m175156[m -> [32m443487[m bytes
[31m|[m  7 files changed, 43 insertions(+), 22 deletions(-)
[31m|[m 
* [33mcommit 78c9c1e64277315b244c11133482b05147f9dcbe[m
[31m|[m Author: guiyom <guiyom@PC2>
[31m|[m Date:   Fri Aug 9 23:51:24 2019 +0800
[31m|[m 
[31m|[m     [interface] new date interval selector + improvements
[31m|[m     
[31m|[m     * get_user_date deprecated: use of simpledialog.askdate instead
[31m|[m     * askperiod added to simpledialog
[31m|[m     * scrollbar in MultiSelectorFrame
[31m|[m     * added an option in _format_list_to_dict to avoid errors
[31m|[m 
[31m|[m  tools/helpers/advanced_utils/date_utils.py   |  13 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/__init__.py          |   8 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/advanced_wrappers.py |  11 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/basics.py            |  25 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/custom_dialog.py     |  68 [32m++++[m[31m-[m
[31m|[m  tools/helpers/interface/date_picker.py       | 251 [32m++++++++++++++[m[31m---[m
[31m|[m  tools/helpers/interface/wrappers.py          |  22 [32m+[m[31m-[m
[31m|[m  7 files changed, 317 insertions(+), 81 deletions(-)
[31m|[m 
* [33mcommit 8e2fcf6cfa58bd2edd08a67aa5c962b3fec6cb75[m
[31m|[m Author: guiyom-e <46320048+guiyom-e@users.noreply.github.com>
[31m|[m Date:   Thu Aug 1 23:59:10 2019 +0800
[31m|[m 
[31m|[m     Set theme jekyll-theme-cayman
[31m|[m 
[31m|[m  docs/_config.yml | 1 [32m+[m
[31m|[m  1 file changed, 1 insertion(+)
[31m|[m 
* [33mcommit d51264b25de74d2670916067a32844b9bb1db5c3[m
[31m|[m Author: guiyom <guiyom@PC2>
[31m|[m Date:   Thu Aug 1 20:52:26 2019 +0800
[31m|[m 
[31m|[m     [advanced_utils] in get_periods, nb_period can be None + improvements
[31m|[m 
[31m|[m  build/inno_setup_script.iss                |  2 [32m+[m[31m-[m
[31m|[m  tools/__init__.py                          |  2 [32m+[m[31m-[m
[31m|[m  tools/helpers/advanced_utils/date_utils.py | 39 [32m++++++++++++[m[31m--------[m
[31m|[m  3 files changed, 25 insertions(+), 18 deletions(-)
[31m|[m 
* [33mcommit 3fffb6fec6e7fabe9b0fa1b82408bbfb1555735b[m
[31m|[m Author: guiyom <guiyom@PC2>
[31m|[m Date:   Thu Aug 1 01:01:15 2019 +0800
[31m|[m 
[31m|[m     [doc] improved doc + requirement bug fix
[31m|[m     
[31m|[m     * new numpy 1.17.0 not supported by pyinstaller 3.4 --> 1.16.2
[31m|[m     * pandas 0.25.0 downgraded to 0.24.2
[31m|[m 
[31m|[m  .gitignore                  |   4 [32m+[m[31m-[m
[31m|[m  build/inno_setup_script.iss |   7 [32m+[m[31m-[m
[31m|[m  conf.py                     |  13 [32m+[m[31m-[m
[31m|[m  index.rst                   |  29 [32m++++[m[31m-[m
[31m|[m  requirements.txt            |   4 [32m+[m[31m-[m
[31m|[m  setup.bat                   | 223 [32m+++++++++++++++++++[m[31m---------------[m
[31m|[m  tools/__init__.py           |   2 [32m+[m[31m-[m
[31m|[m  7 files changed, 168 insertions(+), 114 deletions(-)
[31m|[m 
* [33mcommit 38755969f78cd5bec036f25f81cc5c46c436555c[m
[31m|[m Author: guiyom <guiyom@PC2>
[31m|[m Date:   Tue Jul 30 20:39:01 2019 +0800
[31m|[m 
[31m|[m     [doc] added doc + autodoc with sphinx
[31m|[m 
[31m|[m  conf.py                                      |  54 [32m+++[m
[31m|[m  index.rst                                    |  21 [32m+[m
[31m|[m  requirements.txt                             |   9 [32m+[m
[31m|[m  tools/__init__.py                            |  37 [32m+[m[31m-[m
[31m|[m  tools/exceptions.py                          |   4 [32m+[m[31m-[m
[31m|[m  tools/helpers/__init__.py                    |   9 [32m+[m[31m-[m
[31m|[m  tools/helpers/advanced_utils/__init__.py     |   8 [32m+[m[31m-[m
[31m|[m  .../advanced_utils/dataframe_utils.py        |  97 [32m++++[m
[31m|[m  tools/helpers/advanced_utils/date_utils.py   |   4 [32m+[m[31m-[m
[31m|[m  tools/helpers/config_manager/__init__.py     |  69 [32m++[m[31m-[m
[31m|[m  .../config_manager/config_conversion.py      |  14 [32m+[m[31m-[m
[31m|[m  tools/helpers/config_manager/config_dict.py  |   6 [32m+[m[31m-[m
[31m|[m  .../helpers/config_manager/config_models.py  |  10 [32m+[m[31m-[m
[31m|[m  tools/helpers/data_manager/__init__.py       |   5 [32m+[m[31m-[m
[31m|[m  tools/helpers/data_manager/data_loader.py    |  24 [32m+[m[31m-[m
[31m|[m  tools/helpers/data_manager/data_writer.py    |  13 [32m+[m[31m-[m
[31m|[m  tools/helpers/data_manager/file_utils.py     |   6 [32m+[m[31m-[m
[31m|[m  .../helpers/data_manager/filepath_manager.py |  33 [32m+[m[31m-[m
[31m|[m  tools/helpers/data_manager/plots.py          |   6 [32m+[m
[31m|[m  tools/helpers/interface/__init__.py          |  44 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/advanced_wrappers.py |  16 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/anomalies.py         |   9 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/basics.py            |   5 [32m+[m
[31m|[m  tools/helpers/interface/custom_dialog.py     |   6 [32m+[m
[31m|[m  tools/helpers/interface/custom_messagebox.py |   8 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/date_picker.py       |  15 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/logger_widget.py     |  14 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/main_interface.py    |   8 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/text_frame.py        |   8 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/tooltip.py           |  15 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/wrappers.py          |  31 [32m+[m[31m-[m
[31m|[m  tools/helpers/models/__init__.py             |   8 [32m+[m[31m-[m
[31m|[m  tools/helpers/models/dict_models.py          |  18 [32m+[m[31m-[m
[31m|[m  tools/helpers/models/metaclasses.py          |  19 [32m+[m[31m-[m
[31m|[m  tools/helpers/models/path_models.py          | 410 [32m+[m[31m----------------[m
[31m|[m  tools/helpers/models/str_models.py           | 331 [32m+++++++++++++[m
[31m|[m  tools/helpers/models/types_models.py         | 113 [32m++++[m[31m-[m
[31m|[m  tools/helpers/utils/__init__.py              |   7 [32m+[m[31m-[m
[31m|[m  tools/helpers/utils/decorators.py            |  27 [32m+[m[31m-[m
[31m|[m  tools/helpers/utils/module_utils.py          |  20 [32m+[m[31m-[m
[31m|[m  tools/helpers/utils/utils.py                 |  21 [32m+[m
[31m|[m  tools/logger.py                              |   2 [32m+[m
[31m|[m  tools/tests/__init__.py                      |   5 [32m+[m
[31m|[m  43 files changed, 1057 insertions(+), 532 deletions(-)
[31m|[m 
* [33mcommit e60eef4af5dff29b35e94999c78bce25e3820270[m
[31m|[m Author: guiyom <guillaume.egee@bluesg.com.sg>
[31m|[m Date:   Tue Jul 30 19:10:14 2019 +0800
[31m|[m 
[31m|[m     [dev] minor improvements and bug fixes (date_utils)
[31m|[m 
[31m|[m  tools/__init__.py                              |  2 [32m+[m[31m-[m
[31m|[m  tools/helpers/advanced_utils/date_utils.py     |  2 [32m+[m[31m-[m
[31m|[m  tools/helpers/data_manager/data_writer.py      | 14 [32m++++++++[m[31m------[m
[31m|[m  tools/helpers/data_manager/filepath_manager.py |  2 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/custom_dialog.py       | 12 [32m++++++[m[31m------[m
[31m|[m  tools/helpers/interface/custom_messagebox.py   |  2 [32m++[m
[31m|[m  tools/helpers/interface/main_interface.py      |  2 [32m+[m[31m-[m
[31m|[m  7 files changed, 20 insertions(+), 16 deletions(-)
[31m|[m 
* [33mcommit 660d74b3fec1b83a2837d5ac2085880d84499f4c[m
[31m|[m Author: guiyom <guiyom@PC2>
[31m|[m Date:   Tue Jul 30 02:32:40 2019 +0800
[31m|[m 
[31m|[m     [repo] updated requirements
[31m|[m     
[31m|[m     * removed pywin32 (not supported on linux)
[31m|[m     * updated to pandas 0.25 and numpy 1.17
[31m|[m 
[31m|[m  requirements.txt | 180 [32m++++++++++++++++++++++[m[31m-----------------------[m
[31m|[m  1 file changed, 90 insertions(+), 90 deletions(-)
[31m|[m 
* [33mcommit 74fac16d074e4efe14276c880fb2c24a4cf73498[m
[31m|[m Author: guiyom <guiyom@PC2>
[31m|[m Date:   Tue Jul 30 02:28:39 2019 +0800
[31m|[m 
[31m|[m     [interface] v1.2 big refacto + Dialog instead of Tk
[31m|[m     
[31m|[m     * wording: 'Dialog', 'choices' no more 'Selector' or 'Tk', 'answers'
[31m|[m     * advanced messagebox, simpledialog, filedialog
[31m|[m     * removed identity_dict from models (already in dict_models)
[31m|[m 
[31m|[m  build/inno_setup_script.iss                  | 252 [32m+++++++[m[31m-------[m
[31m|[m  main.bat                                     |   2 [32m+[m[31m-[m
[31m|[m  main.py                                      | 203 [32m+++++[m[31m------[m
[31m|[m  tools/__init__.py                            |   4 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/__init__.py          |  20 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/advanced_wrappers.py |  64 [32m++++[m
[31m|[m  tools/helpers/interface/anomalies.py         | 262 [32m+++++++[m[31m--------[m
[31m|[m  tools/helpers/interface/basics.py            | 167 [32m+[m[31m--------[m
[31m|[m  ...lector_messagebox.py => custom_dialog.py} | 206 [32m++++++[m[31m------[m
[31m|[m  tools/helpers/interface/custom_messagebox.py | 118 [32m+++[m[31m----[m
[31m|[m  tools/helpers/interface/date_picker.py       |   9 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/main_interface.py    |  18 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/text_frame.py        |  22 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/wrappers.py          | 297 [32m++++++++++++++[m[31m---[m
[31m|[m  tools/helpers/models/identity_dict.py        |  15 [31m-[m
[31m|[m  15 files changed, 875 insertions(+), 784 deletions(-)
[31m|[m 
* [33mcommit 4903c46ab56d4edecc727c6605755814b40e8e45[m
[31m|[m Author: guiyom <guiyom@PC2>
[31m|[m Date:   Tue Jul 30 01:24:11 2019 +0800
[31m|[m 
[31m|[m     [data_loader] minor improvements, added ask_header arg
[31m|[m 
[31m|[m  tools/helpers/data_manager/__init__.py       |   9 [32m+[m[31m-[m
[31m|[m  tools/helpers/data_manager/data_loader.py    | 165 [32m++[m[31m--[m
[31m|[m  tools/helpers/data_manager/file_utils.py     | 234 [32m++[m[31m---[m
[31m|[m  .../helpers/data_manager/filepath_manager.py | 797 [32m+++++++++[m[31m--------[m
[31m|[m  4 files changed, 610 insertions(+), 595 deletions(-)
[31m|[m 
* [33mcommit 0aa4259dfdf95ca88d1a2b2bead223e5355c96dc[m
[31m|[m Author: guiyom <guiyom@PC2>
[31m|[m Date:   Tue Jul 30 01:20:50 2019 +0800
[31m|[m 
[31m|[m     [utils] moved date_utils to advanced_utils
[31m|[m     
[31m|[m     * new util isinlist
[31m|[m     * bug fix in get_period
[31m|[m 
[31m|[m  tools/__init__.py                            |   3 [32m+[m[31m-[m
[31m|[m  tools/helpers/advanced_utils/__init__.py     |  15 [32m+[m
[31m|[m  .../{utils => advanced_utils}/date_utils.py  | 910 [32m++++++++[m[31m---------[m
[31m|[m  tools/helpers/utils/__init__.py              |  43 [32m+[m[31m-[m
[31m|[m  tools/helpers/utils/utils.py                 | 310 [32m+++[m[31m---[m
[31m|[m  5 files changed, 656 insertions(+), 625 deletions(-)
[31m|[m 
* [33mcommit be69d30879883f9743bfd361abf541e4854dcb40[m
[31m|[m Author: guiyom <guiyom@PC2>
[31m|[m Date:   Sat Jul 27 14:06:01 2019 +0800
[31m|[m 
[31m|[m     [interface] new selector with check boxes and radio buttons
[31m|[m     
[31m|[m     * new selector, added to messagebox
[31m|[m     * selector renamed in selector_frames
[31m|[m     * new file: basics
[31m|[m     * minor improvements
[31m|[m 
[31m|[m  tools/__init__.py                            |    2 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/__init__.py          |   79 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/basics.py            |  193 [32m+++[m
[31m|[m  tools/helpers/interface/custom_messagebox.py |  313 [32m++[m[31m---[m
[31m|[m  tools/helpers/interface/date_picker.py       | 1160 [32m++++++++[m[31m--------[m
[31m|[m  tools/helpers/interface/logger_widget.py     |  117 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/main_interface.py    |  397 [32m+++[m[31m---[m
[31m|[m  tools/helpers/interface/selector.py          |   20 [31m-[m
[31m|[m  .../helpers/interface/selector_messagebox.py |  335 [32m+++++[m
[31m|[m  tools/helpers/interface/text_frame.py        |   62 [32m+[m[31m-[m
[31m|[m  tools/helpers/interface/wrappers.py          |  229 [32m+[m[31m--[m
[31m|[m  11 files changed, 1718 insertions(+), 1189 deletions(-)
[31m|[m 
* [33mcommit 0c2c62bd0bcfcf49a637f36cea0b56e3f8c69bca[m
[31m|[m Author: guiyom <guiyom@PC2>
[31m|[m Date:   Sat Jul 27 13:42:58 2019 +0800
[31m|[m 
[31m|[m     [config_manager] improvements
[31m|[m     
[31m|[m     * added default option in __call__ method
[31m|[m     * moved BaseDict to models
[31m|[m     * added how_section arg in reload_default to allow advanced merge
[31m|[m 
[31m|[m  tools/helpers/config_manager/__init__.py     |  14 [32m+[m[31m--[m
[31m|[m  tools/helpers/config_manager/config_dict.py  |  87 [32m+[m[31m-------------[m
[31m|[m  .../helpers/config_manager/config_models.py  |  55 [32m+++++[m[31m----[m
[31m|[m  tools/helpers/models/__init__.py             |  25 [32m++[m[31m--[m
[31m|[m  tools/helpers/models/dict_models.py          | 104 [32m+++++++++++++++++[m
[31m|[m  5 files changed, 164 insertions(+), 121 deletions(-)
[31m|[m 
* [33mcommit d04d58ce4b30cdf3e63a7dfbf17cef7598f7d25e[m
[31m|[m Author: guiyom <guiyom@PC2>
[31m|[m Date:   Thu Jul 25 19:29:55 2019 +0800
[31m|[m 
[31m|[m     [data_manager] added open directory options
[31m|[m 
[31m|[m  tools/helpers/data_manager/file_utils.py     |  23 [32m++[m[31m-[m
[31m|[m  .../helpers/data_manager/filepath_manager.py | 125 [32m++++++++++++[m[31m-----[m
[31m|[m  2 files changed, 99 insertions(+), 49 deletions(-)
[31m|[m 
* [33mcommit 4546a7cc29f7efa03b97a6573407745e9a0b7f2e[m
[31m|[m Author: guiyom <guillaume.egee@bluesg.com.sg>
[31m|[m Date:   Thu Jul 25 16:41:42 2019 +0800
[31m|[m 
[31m|[m     [data_manager] allow keyword arguments in read_csv + text files read like CSV
[31m|[m 
[31m|[m  tools/helpers/data_manager/__init__.py    | 72 [32m++++++++++[m[31m-----------[m
[31m|[m  tools/helpers/data_manager/data_loader.py |  8 [32m+[m[31m--[m
[31m|[m  2 files changed, 40 insertions(+), 40 deletions(-)
[31m|[m 
* [33mcommit 30f2e54da95511946541bc1f6ee767a2903f3885[m
[31m|[m Author: guiyom <guillaume.egee@bluesg.com.sg>
[31m|[m Date:   Thu Jul 25 15:06:31 2019 +0800
[31m|[m 
[31m|[m     [config_manager] bug fix in reload_default method
[31m|[m 
[31m|[m  tools/helpers/config_manager/__init__.py      | 2 [32m+[m[31m-[m
[31m|[m  tools/helpers/config_manager/config_models.py | 2 [32m+[m[31m-[m
[31m|[m  2 files changed, 2 insertions(+), 2 deletions(-)
[31m|[m 
* [33mcommit 425954afe2f743ff554186ed66df9de121534976[m
[31m|[m Author: guiyom <guillaume.egee@bluesg.com.sg>
[31m|[m Date:   Thu Jul 25 12:16:16 2019 +0800
[31m|[m 
[31m|[m     [utils] module_utils: bug fix: reloading lambda function
[31m|[m 
[31m|[m  tools/__init__.py                   | 2 [32m+[m[31m-[m
[31m|[m  tools/helpers/utils/module_utils.py | 2 [32m++[m
[31m|[m  2 files changed, 3 insertions(+), 1 deletion(-)
[31m|[m 
* [33mcommit 213732da601ef7a45e04646763aaaa3bee4771de[m
[31m|[m Author: guiyom <guiyom@PC2>
[31m|[m Date:   Thu Jul 25 09:31:19 2019 +0800
[31m|[m 
[31m|[m     [models] Path models bug fix: method applied to collection
[31m|[m     
[31m|[m     decorator keep_type allow to apply a method on a collection and return
[31m|[m     an object of type collection. Without a decorator, a list is returned.
[31m|[m 
[31m|[m  tools/__init__.py                    | 144 [32m+++++++++[m[31m---------[m
[31m|[m  tools/helpers/models/metaclasses.py  |  32 [32m+++[m[31m-[m
[31m|[m  tools/helpers/models/path_models.py  | 203 [32m++++++++++++++++++++[m[31m-----[m
[31m|[m  tools/helpers/models/types_models.py |  58 [32m+++++[m[31m--[m
[31m|[m  4 files changed, 308 insertions(+), 129 deletions(-)
[31m|[m 
* [33mcommit cd961dfee3676425c72ae427c5b3244e33c83f7c[m
[31m|[m Author: guiyom <guillaume.egee@bluesg.com.sg>
[31m|[m Date:   Tue Jul 23 09:53:39 2019 +0800
[31m|[m 
[31m|[m     [utils] date_utils: minor bug fix + None period_type
[31m|[m 
[31m|[m  tools/__init__.py                 |  2 [32m+[m[31m-[m
[31m|[m  tools/helpers/utils/date_utils.py | 19 [32m++++++++++++++[m[31m-----[m
[31m|[m  2 files changed, 15 insertions(+), 6 deletions(-)
[31m|[m 
* [33mcommit f58c8ead629d4633d86bc693a2be6368ea80b130[m
[31m|[m Author: guiyom <guiyom@PC2>
[31m|[m Date:   Wed Jul 24 09:49:45 2019 +0800
[31m|[m 
[31m|[m     [models] Path and PathCollection rewritten
[31m|[m 
[31m|[m  tools/__init__.py                   |   2 [32m+[m[31m-[m
[31m|[m  tools/helpers/models/__init__.py    |   2 [32m+[m[31m-[m
[31m|[m  tools/helpers/models/metaclasses.py |  25 [32m+[m
[31m|[m  tools/helpers/models/path_models.py | 868 [32m+++++++++++++++[m[31m-----------[m
[31m|[m  tools/helpers/models/singleton.py   |   9 [31m-[m
[31m|[m  5 files changed, 533 insertions(+), 373 deletions(-)
[31m|[m 
* [33mcommit f73ac50b3325f37c2f04ab27d93724fdc2bfd9c3[m
[31m|[m Author: guiyom <guiyom@PC2>
[31m|[m Date:   Tue Jul 23 00:43:39 2019 +0800
[31m|[m 
[31m|[m     [setup] updated setup for better ux + bug fix
[31m|[m 
[31m|[m  .gitignore                  |  3 [32m+[m[31m-[m
[31m|[m  build/inno_setup_script.iss |  2 [32m+[m[31m-[m
[31m|[m  docs/.keep                  |  1 [32m+[m
[31m|[m  main.bat                    |  7 [32m+[m[31m--[m
[31m|[m  setup.bat                   | 98 [32m+++++++++++++++++++++++++++++++++[m[31m--[m
[31m|[m  tools/__init__.py           |  3 [32m+[m[31m-[m
[31m|[m  6 files changed, 102 insertions(+), 12 deletions(-)
[31m|[m 
* [33mcommit 016684baa2973ad00f36282d90863c209dbeb26d[m
[31m|[m Author: guiyom-e <46320048+guiyom-e@users.noreply.github.com>
[31m|[m Date:   Thu Jul 18 22:27:52 2019 +0800
[31m|[m 
[31m|[m     [init] v1.0.0
[31m|[m     
[31m|[m     added files
[31m|[m 
[31m|[m  .gitignore                                   |  11 [32m+[m
[31m|[m  README.md                                    |  27 [32m+[m[31m-[m
[31m|[m  build/inno_setup_script.iss                  | 127 [32m++++[m
[31m|[m  data/.keep                                   |   1 [32m+[m
[31m|[m  main.bat                                     |   7 [32m+[m
[31m|[m  main.py                                      | 101 [32m+++[m
[31m|[m  main.spec                                    |  37 [32m+[m
[31m|[m  requirements.txt                             |  90 [32m+++[m
[31m|[m  scripts/__init__.py                          |   6 [32m+[m
[31m|[m  scripts/sample.py                            |  28 [32m+[m
[31m|[m  setup.bat                                    |   5 [32m+[m
[31m|[m  ...ools-3DF36B5D-694A-4743-96A4-C02B269C95D5 |   1 [32m+[m
[31m|[m  tools/__init__.py                            |  71 [32m++[m
[31m|[m  tools/config/config.ini.default              |   2 [32m+[m
[31m|[m  tools/exceptions.py                          |  18 [32m+[m
[31m|[m  tools/favicon.ico                            | Bin [31m0[m -> [32m175156[m bytes
[31m|[m  tools/helpers/__init__.py                    |   7 [32m+[m
[31m|[m  tools/helpers/config_manager/__init__.py     |   7 [32m+[m
[31m|[m  .../config_manager/config_conversion.py      | 333 [32m++++++++[m
[31m|[m  tools/helpers/config_manager/config_dict.py  | 668 [32m+++++++++++++++++[m
[31m|[m  .../helpers/config_manager/config_models.py  | 589 [32m+++++++++++++++[m
[31m|[m  tools/helpers/data_manager/__init__.py       |  36 [32m+[m
[31m|[m  tools/helpers/data_manager/data_loader.py    |  79 [32m++[m
[31m|[m  tools/helpers/data_manager/data_writer.py    | 106 [32m+++[m
[31m|[m  tools/helpers/data_manager/file_utils.py     | 118 [32m+++[m
[31m|[m  .../helpers/data_manager/filepath_manager.py | 346 [32m+++++++++[m
[31m|[m  tools/helpers/data_manager/plots.py          |  22 [32m+[m
[31m|[m  tools/helpers/interface/__init__.py          |  31 [32m+[m
[31m|[m  tools/helpers/interface/anomalies.py         | 131 [32m++++[m
[31m|[m  tools/helpers/interface/custom_messagebox.py | 167 [32m+++++[m
[31m|[m  tools/helpers/interface/date_picker.py       | 581 [32m++++++++++++++[m
[31m|[m  tools/helpers/interface/logger_widget.py     |  59 [32m++[m
[31m|[m  tools/helpers/interface/main_interface.py    | 199 [32m+++++[m
[31m|[m  tools/helpers/interface/selector.py          |  20 [32m+[m
[31m|[m  tools/helpers/interface/text_frame.py        |  23 [32m+[m
[31m|[m  tools/helpers/interface/tooltip.py           |  56 [32m++[m
[31m|[m  tools/helpers/interface/wrappers.py          | 108 [32m+++[m
[31m|[m  tools/helpers/models/__init__.py             |  16 [32m+[m
[31m|[m  tools/helpers/models/identity_dict.py        |  15 [32m+[m
[31m|[m  tools/helpers/models/path_models.py          | 362 [32m+++++++++[m
[31m|[m  tools/helpers/models/singleton.py            |   9 [32m+[m
[31m|[m  tools/helpers/models/types_models.py         |  10 [32m+[m
[31m|[m  tools/helpers/utils/__init__.py              |  26 [32m+[m
[31m|[m  tools/helpers/utils/date_utils.py            | 446 [32m+++++++++++[m
[31m|[m  tools/helpers/utils/decorators.py            |  72 [32m++[m
[31m|[m  tools/helpers/utils/module_utils.py          | 105 [32m+++[m
[31m|[m  tools/helpers/utils/utils.py                 | 143 [32m++++[m
[31m|[m  tools/logger.py                              | 110 [32m+++[m
[31m|[m  tools/logs/.keep                             |   1 [32m+[m
[31m|[m  tools/src/.keep                              |   1 [32m+[m
[31m|[m  tools/src/readme.txt                         |   1 [32m+[m
[31m|[m  tools/troubleshooting/req_pip_1              |  25 [32m+[m
[31m|[m  tools/troubleshooting/requirements.txt       |  90 [32m+++[m
[31m|[m  tools/troubleshooting/troubleshooting.md     |  87 [32m+++[m
[31m|[m  tools/troubleshooting/uninstall_conda_1      |  26 [32m+[m
[31m|[m  55 files changed, 5762 insertions(+), 1 deletion(-)
[31m|[m 
* [33mcommit 144fb69d623a27243694db2b928f9bba4a3a707f[m
  Author: guiyom-e <46320048+guiyom-e@users.noreply.github.com>
  Date:   Thu Jun 20 01:32:21 2019 +0800
  
      Initial commit
  
   README.md | 2 [32m++[m
   1 file changed, 2 insertions(+)
