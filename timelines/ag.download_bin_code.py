#!/usr/bin/env python3

from timelines.basis import BasisEvent
from timelines.basis import Commands as cmd
from timelines.basis import logger

#---------------------------------------------------------------------------
#   Definitions
#---------------------------------------------------------------------------

#
# _version indicates downloading binary code version
#
_version = '3.0.0-alpha4'

class CustomEvent(BasisEvent):

    #override
    def action(self):
        logger.info('--> timelines.ag.download_bin_code <--')

        folder = ys['codepath']

        if not os.path.exists(folder):
            os.makedirs(folder)

        if not os.path.isdir(folder):
            logger.error('\'codepath\' does not indicate a folder in setting file.')
            return False

        loadpath = "http://www-eu.apache.org/dist/hadoop/common/hadoop-{0}/hadoop-{0}.tar.gz" % (_version)

        shell = "curl -sSL {0} | tar -C {1} -xzv" % (loadpath, folder)
        res = cmd.do(shell)
        if res != 0:
            return False

        return True

def download_bin_code(ys):
    return CustomEvent(ys).occur(attempts=3, interval=3)