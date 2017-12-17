#!/usr/bin/env python3

from scripts.basis import Basis
from scripts.basis import logger
from scripts.command import Command as cmd
import os
import copy

#---------------------------------------------------------------------------
#   Definitions
#---------------------------------------------------------------------------

class Custom(Basis):

    # override
    def action(self):
        logger.info('--> controlp.distribute_binary_package<--')

        ssh_option = 'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5'

        nodes_list_with_username = list()

        roles_without_controller = dict(filter(lambda x: x[0] != 'controlp',
            self.ys['roles'].items()))
        for k, v in roles_without_controller.items():
            nodes_list_with_username.extend([ v['usr'] + '@' + n for n in v['hosts'] ])

        nodes_list_with_username = list(set(nodes_list_with_username))


        #
        # add permissions
        #
        usr_host_list = copy.deepcopy(nodes_list_with_username)
        for k, v in roles_without_controller.items():
            for host in v['hosts']:
                usr_host = (v['usr']+'@'+host)

                if usr_host in usr_host_list:
                    usr_host_list.remove(usr_host)
                    
                    ins = "{0} {1} -tt 'sudo -S chown -R {2} /opt/' ".format(
                            ssh_option, usr_host, v['usr'])
                    retcode = cmd.sudo(ins, v['pwd'])
                    logger.info("ins: %s; retcode: %d." % (ins, retcode))

        #
        # binary code
        #
        master_sour_folder = os.path.join(self.ys['sourcecode'],
                'hadoop-dist/target/hadoop-3.0.0-beta1/')
        slave_dest_folder = os.path.join(self.ys['binarycode'], 'rose-on-yarn/')

        for node_with_username in nodes_list_with_username:
            ins = "ssh {2} 'mkdir -p {3}' && rsync -e '{0}' -az '{1}' {2}:{3} & sleep 0.5".format(
                    ssh_option, master_sour_folder,
                    node_with_username, slave_dest_folder)
            retcode = cmd.do(ins)
            logger.info("ins: %s; retcode: %d." % (ins, retcode))

        # #
        # # configs
        # #
        # master_configs = './configs/*.xml'
        # slave_dest_configs_folder = os.path.join(self.ys['binarycode'], 'rose-on-yarn/etc/hadoop/')

        # for node_with_username in nodes_list_with_username:
        #     ins = "ssh {2} 'mkdir -p {3}' && rsync -e '{0}' -az '{1}' {2}:{3} & sleep 0.5".format(
        #             ssh_option, master_configs,
        #             node_with_username, slave_dest_configs_folder)
        #     retcode = cmd.do(ins)
        #     logger.info("ins: %s; retcode: %d." % (ins, retcode))

        #
        # scripts about building env
        #
        master_scripts = './utilities/'
        slave_scripts_folder = os.path.join(self.ys['binarycode'], 'scripts/')

        for node_with_username in nodes_list_with_username:
            ins = "ssh {2} 'mkdir -p {3}' && rsync -e '{0}' -az '{1}' {2}:{3} & sleep 0.5".format(
                    ssh_option, master_scripts,
                    node_with_username, slave_scripts_folder)
            retcode = cmd.do(ins)
            logger.info("ins: %s; retcode: %d." % (ins, retcode))

        #
        # wait to end
        #
        ins = 'wait'
        retcode = cmd.do(ins)
        if retcode != 0:
            return False

        return True


def trigger(ys):
    e = Custom(ys, attempts=3, interval=3, auto=True)
    return e.status
