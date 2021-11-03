# -*- coding: utf-8 -*-
import commands
import sys,os
import argparse
import logging

# Return:
#   0 Successful.
#   255 Parse GPU count failed.
#   254 Parse Current GPU clock value failed.
#   253 Set auto boost failed.
#   252 Set UNRESTRICTED failed.
#   251 Set max clock/mem failed.


def initlog(logfile=None, level=None, log_stdout=True):
    """
    Initialize the log, default log level is NOTSET, it will write the log
    message into logfile, and also print onto the screen.
    If set log_stdout to False, will not print the log message onto the screen.
    """
    log_levels = {'debug': logging.DEBUG,
                  'info': logging.INFO,
                  'warn': logging.WARN,
                  'warning': logging.WARNING,
                  'error': logging.ERROR,
                  'fatal': logging.FATAL,
                  'critical': logging.CRITICAL}
    log = logging.getLogger()
    if level not in log_levels:
        print("ERROR: Invalid log level specified")
        print("ERROR: Try to use the default one: debug")
        level = 'debug'
    if logfile is None and not log_stdout:
        print("ERROR: At least one of logfile and log_stdout is required")
        raise Exception('Specify logfile or log_stdout for logging')
    log_level = log_levels.get(level, logging.NOTSET)
    log.setLevel(log_level)
    # Customize the log format
    fmt = logging.Formatter('%(asctime)s %(levelname)-5.5s: %(message)s',
                            '%Y-%m-%d %H:%M:%S')
    # Write the log message into logfile
    if logfile:
        file_log_handler = logging.FileHandler(logfile)
        log.addHandler(file_log_handler)
        file_log_handler.setFormatter(fmt)
    # Print the log message onto the screen
    if log_stdout:
        screen_log_handler = logging.StreamHandler()
        log.addHandler(screen_log_handler)
        screen_log_handler.setFormatter(fmt)
    return log


def commands_run_on_local(cmd, password=None):
    logging.debug("Run: %s" % cmd)
    if password is None:
        status, res = commands.getstatusoutput(cmd)
    else:
        status, res = commands.getstatusoutput("echo %s | sudo -S %s" % (password, cmd))
    logging.info(res)
    return status, res


def get_gpu_applications(gid):
    status, app = commands_run_on_local("nvidia-smi --query-gpu=clocks.applications.graphics,clocks.applications.mem \
    -i %s --format=csv,noheader,nounits" % gid)
    if status != 0:
        logging.error("Parse %s applications values failed." % gid)
        sys.exit(254)
    else:
        apps = app.split(",")
        return apps[0].strip(), apps[1].strip()


def set_gpu_clock_max(gid, gra, mem):
    code, res = commands_run_on_local("nvidia-smi -i %s -ac %s,%s" % (gid, mem, gra))
    if code == 0:
        applications = get_gpu_applications(gid)
        if applications[0] != gra:
            logging.error("[%s] FAIL!!! (current clock:%s, application clock:%s)" % (gid, applications[0], gra))
            return False
        else:
            logging.info("[%s] SUCCESS: current clock:%s, application clock:%s" % (gid, applications[0], gra))

        if applications[1] != mem:
            logging.error("[%s] FAIL.(current mem:%s, application mem:%s)" % (gid, applications[1], mem))
            return False
        else:
            logging.info("[%s] SUCCESS: current mem:%s, application mem:%s" % (gid, applications[1], mem))
    else:
        return False

    return True

def simply_enable_linux_nvidia_persistenced(pwd=None):
    """
    Enable nvidia-persistenced like below:
        1: Start nvidia-persistenced service
        2: Run /usr/bin/nvidia-persistenced
        3: nvidia-smi pm 1
    """
    if os.path.isfile('/bin/systemctl'):
        commands_run_on_local("echo %s | sudo -S /bin/systemctl start nvidia-persistenced" % pwd)
        commands_run_on_local("echo %s | sudo -S /bin/systemctl status nvidia-persistenced" % pwd)
    else:
        commands_run_on_local("echo %s | sudo -S service nvidia-persistenced start" % pwd)
        commands_run_on_local("echo %s | sudo -S service nvidia-persistenced status" % pwd)
    commands_run_on_local("echo %s | sudo -S nvidia-persistenced --verbose" % pwd)
    commands_run_on_local("echo %s | sudo -S nvidia-smi -pm 1" % pwd)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--password", nargs='?', dest="pwd", required=True, help='Local user password.')
    args = parser.parse_args()
    pwd = args.pwd
    logger = initlog(logfile=None, level='info')
    simply_enable_linux_nvidia_persistenced(pwd)
    status, res = commands_run_on_local("echo %s | sudo -S nvidia-smi -acp UNRESTRICTED" % pwd)
    if status != 0:
        logging.error("Set UNRESTRICTED failed.")
        sys.exit(252)

    status, gcount = commands_run_on_local("nvidia-smi --query-gpu=count --format=csv,noheader | uniq")
    if status == 0 :
        logging.info("There are %s gpus." % gcount)
    else:
        logging.error("Parse gpu count failed.")
        sys.exit(255)

    set_res = 0
    for gpu_index in range(0, int(gcount)):
        status, max = commands_run_on_local("nvidia-smi --query-gpu=clocks.max.graphics,clocks.max.mem -i %s \
        --format=csv,noheader,nounits" % gpu_index)
        if status != 0:
            logging.error("Get %s max clock value failed." % gpu_index)
        else:
            maxs = max.split(",")

        status = set_gpu_clock_max(gpu_index, maxs[0].strip(), maxs[1].strip())
        if not status:
            set_res = 1

        status, gpu_t = commands_run_on_local("nvidia-smi --query-gpu=gpu_name --format=csv,noheader -i %s" % gpu_index)
        if "Tesla K80" in gpu_t or "Tesla M40" in gpu_t:
            status, auto_boot = commands_run_on_local("nvidia-smi -i %s --auto-boost-default=0" % gpu_index)
            if status !=0:
                logging.error("Set %s auto boot failed." % gpu_index)
                sys.exit(253)

    if set_res == 1:
        sys.exit(251)
