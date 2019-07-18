from matplotlib import pyplot as plt

from tools.logger import logger
from tools.helpers.data_manager.filepath_manager import save_file


def save_plot(plot_path, overwrite='overwrite', **save_file_kwargs):
    extension = save_file_kwargs.pop('extension', '.png')  # extension in save_file_kwargs is not recommended
    output_path = save_file(plot_path, overwrite=overwrite, extension=extension, **save_file_kwargs)
    plt.savefig(output_path)
    plt.clf()
    return output_path


def save_error_graph(plot_path, err_msg=None, **save_file_kwargs):
    if err_msg is None:
        err_msg = 'Unknown error.'
    logger.error("Plot of {} failed. Error: '{}'".format(plot_path, err_msg))
    _fig = plt.figure(figsize=(21.28, 12))
    plt.text(0.35, 0.5, 'Error on this graph', dict(size=30))
    output_path = save_plot(plot_path, **save_file_kwargs)
    return output_path
