import os
import subprocess
import shlex
import time
from datetime import timedelta


def run_command(command, logfile=None, elapsed=True):
    """

    :param command:
    :param logfile:
    :param elapsed:
    :return:
    """

    currtime = time.time()

    if os.name == "nt":
        process = subprocess.run(command, stderr=subprocess.PIPE)
    else:
        process = subprocess.run(shlex.split(command), stderr=subprocess.PIPE)

    return_code = process.returncode

    if return_code != 0 and logfile is not None:
        with open(str(logfile), "w") as file:
            for line in process.stderr.decode().splitlines():
                file.write(f"{line}\n")

    if elapsed:
        timer(currtime)

    return process.returncode


def timer(start):
    """A helper function to print a time elapsed statement

    :param start:
    :type start:
    :return:
    :rtype: str
    """

    elapsed = time.time() - start
    # logger.debug(f"Time elapsed: {timedelta(seconds=elapsed)}")
    print(f"Time elapsed: {timedelta(seconds=elapsed)}")
