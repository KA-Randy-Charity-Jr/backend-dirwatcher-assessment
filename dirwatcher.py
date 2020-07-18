import argparse
import signal
import time
import os
import logging


__author__ = "Randy Charity Jr"

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')
exit_flag = False


def create_parser():
    """
    create argument parser for command
    line arguments.
    """
    parser = argparse.ArgumentParser(
        description="watches dir for magic string")
    parser.add_argument('dir', help="directory to watch")
    parser.add_argument('magic_string', help="the magical string to look for")
    parser.add_argument(
        '-ext', type=str, default=".txt",
        help="use to fiter for a specific file extension")
    parser.add_argument('-p', type=int, default=1.0,
                        help="polling interval(use integer)")

    return parser


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT.
    Other signals can be mapped here as well (SIGHUP?)
    Basically, it just sets a global flag, and main()
    will exit its loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    # log the associated signal name
    global exit_flag
    logging.warning('Received ' + signal.Signals(sig_num).name)
    exit_flag = True


def dirwatcher(dir_name, magic_str, poll, **kwargs):
    """
    dirwatcher function scans directory for changes in files
    and searches for a magic string in each file ending with
    specific extension
    """
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    extenstion = kwargs["extenstion"]
    watched_files = []
    found_strings = {}
    start_time = time.time()
    logging.info(f'''\n
    {"-" * 60}\n
    Dirwatcher started at {time.ctime()}\n
    {"-" * 60}''')
    global exit_flag
    while not exit_flag:
        try:
            if len(watched_files) > 1 and len(found_strings) > 1:
                watched_files = os.listdir(dir_name)
                found_strings = {key: [] for key in os.listdir(dir_name)}
            else:
                pass
            for file in os.listdir(dir_name):

                if file not in watched_files:
                    logging.info(f"{file} was recently added")
                    found_strings[file] = []
                    watched_files.append(file)
                f = os.path.join(dir_name, file)

                if file.endswith(extenstion):
                    g = open(f)

                    for i, eachline in enumerate(g):
                        if magic_str in eachline:
                            if i not in found_strings[file]:
                                logging.info(
                                    f'{magic_str} found in {f} at line {i+1}')
                                found_strings[file].append(i)

            for name in watched_files:
                if name in os.listdir(dir_name):
                    pass
                else:

                    logging.info(f"{name} was recently deleted")
                    watched_files.remove(name)
        except FileNotFoundError:
            logging.error(f"{dir_name} not found")
        except Exception as e:
            logging.error(f"Unknown exception: {e}")
        time.sleep(int(poll))
    end_time = time.time()
    up_time = end_time - start_time
    logging.info(f'''\n
    {"-" * 60}\n
    Dirwatcher was ended. Total uptime {up_time}s\n
    {"-" * 60}''')


def main():
    """
    passes argument parser and calls dirwatching function
    """
    parser = create_parser()
    ns = parser.parse_args()

    dirwatcher(ns.dir, ns.magic_string, ns.p, extenstion=ns.ext)


if __name__ == "__main__":
    main()
