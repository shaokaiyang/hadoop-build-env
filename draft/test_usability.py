#!/usr/bin/env python3

from timelines.basis import BasisEvent
from timelines.basis import Commands as cmd
from timelines.basis import logger


class CustomEvent(BasisEvent):

    # override
    def action(self):
        logger.info('--> timelines.ag.compile_prerequisites <--')

        debian_shell = './utilities/t.setup_aliyun_maven_mirror.sh'
        retcode = cmd.do(debian_shell)
        if retcode != 0:
            return False

        debian_shell = 'sudo -S ./utilities/t.install_compile_prerequistes.sh'
        retcode = cmd.sudo(debian_shell, self.ys['roles']['ag']['pwd'])
        if retcode != 0:
            return False

        return True


def runtime_prerequisites(ys):
    return CustomEvent(ys).occur(attempts=3, interval=3)
