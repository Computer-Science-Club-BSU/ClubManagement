import os

# Check if we are on a Unix Computer, A Windows Computer, or Some Other System.
if os.name == 'posix':
    # UNIX Directories
    LOG_DIR = '/var/log/cms/'
    CFG_DIR = '/etc/cms/'
elif os.name == 'nt':
    # Windows Directories
    LOG_DIR = 'C:\\cms\\log\\'
    CFG_DIR = 'C:\\cms\\cfg\\'
else:
    raise Exception('No valid OS Found!')