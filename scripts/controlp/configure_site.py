#!/usr/bin/env python3

from scripts.basis import Basis
from scripts.basis import logger
from scripts.command import Command
import os
import shutil
from lxml import etree as ElementTree
from lxml.etree import Element as Element
from lxml.etree import SubElement as SubElement


def putconfig(file, name, value, description=''):
    root = ElementTree.parse(file).getroot()

    for existing_prop in root.getchildren():
        ename = existing_prop.find('name')
        if ename is not None and ename.text == name:
            edescription = existing_prop.find('description')
            if edescription is not None:
                description = edescription.text
            root.remove(existing_prop)
            break

    property = SubElement(root, 'property')
    if description != '':
        description_elem = SubElement(property, 'description')
        description_elem.text = description

    name_elem = SubElement(property, 'name')
    name_elem.text = name
    value_elem = SubElement(property, 'value')
    value_elem.text = value

    conf_file = open(file, 'wb')
    conf_file.write(ElementTree.tostring(
        root, pretty_print=True, encoding='utf-8'))
    conf_file.close()

    return


class Custom(Basis):

    def action(self):
        logger.info('--> common.configure_site <--')

        ssh_option = '-o StrictHostKeyChecking=no -o ConnectTimeout=5'

        cluster_hadoop_lib_native = self.getClusterHadoopLibNativeDir()
        cluster_hadoop_conf_dir = self.getClusterHadoopConfDir()
        cluster_binary_dir = self.getClusterBinaryDir()
        cluster_hdfs_dir = self.getClusterHdfsDir()
        cluster_log_dir = self.getClusterLogDir()

        #
        # wirte slaves' ip into workers
        #
        slaves_list = self.getSlaveHosts()

        workers = open('./configs/workers', 'w')
        for host in slaves_list:
            workers.write("%s \n" % (host['ip']))
        workers.close()

        #
        # configure *-site.xml
        #
        shutil.copy2('./configs/default/hadoop-core.xml',
                     './configs/core-site.xml')
        shutil.copy2('./configs/default/hadoop-hdfs.xml',
                     './configs/hdfs-site.xml')
        shutil.copy2('./configs/default/hadoop-yarn.xml',
                     './configs/yarn-site.xml')
        shutil.copy2('./configs/default/hadoop-mapred.xml',
                     './configs/mapred-site.xml')

        # log-level
        putconfig(file='./configs/mapred-site.xml',
                  name='mapreduce.map.log.level',
                  value='DEBUG')

        putconfig(file='./configs/mapred-site.xml',
                  name='mapreduce.reduce.log.level',
                  value='DEBUG')

        putconfig(file='./configs/mapred-site.xml',
                  name='yarn.app.mapreduce.am.log.level',
                  value='DEBUG')

        # hdfs
        putconfig(file='./configs/core-site.xml',
                  name='fs.defaultFS',
                  value="hdfs://%s:9000" % self.ys['roles']['namen']['hosts'][0])

        putconfig(file='./configs/hdfs-site.xml',
                  name='dfs.replication',
                  value='3')

        putconfig(file='./configs/hdfs-site.xml',
                  name='dfs.namenode.name.dir',
                  value=os.path.join('file:', cluster_hdfs_dir,
                                     self.ys['roles']['namen']['dir']))

        putconfig(file='./configs/hdfs-site.xml',
                  name='dfs.namenode.checkpoint.dir',
                  value=os.path.join('file:', cluster_hdfs_dir,
                                     self.ys['roles']['namen']['sdir']))

        putconfig(file='./configs/hdfs-site.xml',
                  name='dfs.namenode.checkpoint.edits.dir',
                  value=os.path.join('file:', cluster_hdfs_dir,
                                     self.ys['roles']['namen']['sdir']))

        putconfig(file='./configs/hdfs-site.xml',
                  name='dfs.datanode.data.dir',
                  value=os.path.join('file:', cluster_hdfs_dir,
                                     self.ys['roles']['datan']['dir']))

        # mapreduce
        putconfig(file='./configs/mapred-site.xml',
                  name='mapreduce.task.timeout',
                  value='300000')

        putconfig(file='./configs/mapred-site.xml',
                  name='mapreduce.map.memory.mb',
                  value='1536')

        putconfig(file='./configs/mapred-site.xml',
                  name='mapreduce.map.cpu.vcores',
                  value='1')

        putconfig(file='./configs/mapred-site.xml',
                  name='mapreduce.reduce.memory.mb',
                  value='2048')

        putconfig(file='./configs/mapred-site.xml',
                  name='mapreduce.reduce.cpu.vcores',
                  value='1')

        putconfig(file='./configs/mapred-site.xml',
                  name='mapreduce.framework.name',
                  value='yarn')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.nodemanager.aux-services',
                  value='mapreduce_shuffle')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.nodemanager.env-whitelist',
                  value='JAVA_HOME,HADOOP_COMMON_HOME,HADOOP_HDFS_HOME,HADOOP_CONF_DIR,CLASSPATH_PREPEND_DISTCACHE,HADOOP_YARN_HOME,HADOOP_MAPRED_HOME')

        # yarn
        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.resourcemanager.hostname',
                  value=self.ys['roles']['resourcem']['hosts'][0])

        putconfig(file='./configs/mapred-site.xml',
                  name='yarn.app.mapreduce.am.scheduler.heartbeat.interval-ms',
                  value='3000')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.resourcemanager.nodemanagers.heartbeat-interval-ms',
                  value='3000')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.webapp.ui2.enable',
                  value='false')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.nodemanager.resource.detect-hardware-capabilities',
                  value='true')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.scheduler.minimum-allocation-mb',
                  value='512')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.nodemanager.recovery.enabled',
                  value='true')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.nodemanager.address',
                  value='${yarn.nodemanager.hostname}:45678')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.nodemanager.recovery.supervised',
                  value='true')

        # ROSE: yarn->webapp
        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.resourcemanager.webapp.rrds.dir.cluster',
                  value=self.ys['gmetad']['rrds']['dir'])

        # -- logs and tmp
        putconfig(file='./configs/core-site.xml',
                  name='hadoop.tmp.dir',
                  value=self.getClusterTmpDir())

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.nodemanager.delete.debug-delay-sec',
                  value='86400')  # 86400sec = 1day

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.nodemanager.log.retain-seconds',
                  value='86400')  # 86400sec = 1day

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.log-aggregation-enable',
                  value='true')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.nodemanager.remote-app-log-dir',
                  value=self.getClusterLogDir(subdir='remote-app-logs'))

        # jobhistory
        putconfig(file='./configs/mapred-site.xml',
                  name='mapreduce.jobhistory.address',
                  value="%s:10020" % self.ys['roles']['resourcem']['hosts'][0])

        putconfig(file='./configs/mapred-site.xml',
                  name='mapreduce.jobhistory.webapp.address',
                  value="%s:19888" % self.ys['roles']['resourcem']['hosts'][0])

        putconfig(file='./configs/mapred-site.xml',
                  name='mapreduce.jobhistory.webapp.https.address',
                  value="%s:19890" % self.ys['roles']['resourcem']['hosts'][0])

        putconfig(file='./configs/mapred-site.xml',
                  name='mapreduce.jobhistory.admin.address',
                  value="%s:10033" % self.ys['roles']['resourcem']['hosts'][0])

        # -- timeline service
        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.timeline-service.enabled',
                  value='true') # todo. configue timeline

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.timeline-service.version',
                  value='1.0f')  # 1.0f 1.5f

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.system-metrics-publisher.enabled',
                  value='true')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.timeline-service.generic-application-history.enabled',
                  value='true')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.timeline-service.leveldb-timeline-store.ttl-interval-ms ',
                  value='60000')  # ms

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.timeline-service.hostname',
                  value='${yarn.resourcemanager.hostname}')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.timeline-service.recovery.enabled',
                  value='true')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.timeline-service.ttl-enable',
                  value='true')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.timeline-service.ttl-ms',
                  value='86400000')  # 86400000ms = 1day

        # yarn-support opportunistic container scheduler
        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.resourcemanager.opportunistic-container-allocation.enabled',
                  value='true')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.nodemanager.opportunistic-containers-max-queue-length',
                  value='20')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.nodemanager.container-monitor.interval-ms',
                  value='3000')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.nodemanager.health-checker.interval-ms',
                  value='60000')

        # yarn-support distributed scheduler
        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.nodemanager.distributed-scheduling.enabled',
                  value='true')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.nodemanager.amrmproxy.enabled',
                  value='true')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.nodemanager.amrmproxy.address',
                  value='0.0.0.0:8049')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.nodemanager.amrmproxy.client.thread-count',
                  value='3')

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.resourcemanager.scheduler.address',
                  #value="%s:8030" % self.ys['roles']['resourcem']['hosts'][0])
                  value='0.0.0.0:8049')  # on RM, must change it into rm-ip:8030

        putconfig(file='./configs/yarn-site.xml',
                  name='yarn.nodemanager.amrmproxy.realrm.scheduler.address',
                  value="%s:8030" % self.ys['roles']['resourcem']['hosts'][0],
                  description="SUNXY-ROSE: targets to help AMRMProxy find real RM scheduler address")
        # ROSE
        putconfig(file='./configs/yarn-site.xml',
                 name='yarn.rose.enabled',
                 value='true',
                 description="SUNXY-ROSE: targets to manage opportunistic containers as an overselling method")

        # ROSE: support distributed scheduler: on RM, must change it into rm-ip:8030
        shutil.copy2('./configs/yarn-site.xml',
                     './configs/yarn-rm-site.xml')

        putconfig(file='./configs/yarn-rm-site.xml',
                  name='yarn.resourcemanager.scheduler.address',
                  value="%s:8030" % self.ys['roles']['resourcem']['hosts'][0])

        files = ['./configs/core-site.xml',
                 './configs/hdfs-site.xml',
                 './configs/mapred-site.xml',
                 './configs/yarn-site.xml',
                 './configs/yarn-rm-site.xml']

        ins = " && ".join(map(lambda x: "format_file %s" % x, files))

        retcode = Command.do(ins)

        logger.info("ins: %s; retcode: %d." % (ins, retcode))

        if retcode != 0:
            logger.error(ins)
            return False

        #
        # configure ./etc/hadoop/*.sh
        #
        shutil.copy2('./configs/default/hadoop-env.sh',
                     './configs/hadoop-env.sh')
        hadoop_env_file = './configs/hadoop-env.sh'

        envlist = [
            ['PDSH_RCMD_TYPE', 'ssh'],
            ['JAVA_HOME', '/usr/lib/jvm/java-8-openjdk-amd64/'],
            ['HADOOP_HOME', cluster_binary_dir],
            ['HADOOP_YARN_HOME', cluster_binary_dir],
            ['HADOOP_HDFS_HOME', cluster_binary_dir],
            ['HADOOP_MAPRED_HOME', cluster_binary_dir],
            ['HADOOP_COMMON_HOME', cluster_binary_dir],
            ['HADOOP_COMMON_LIB_NATIVE_DIR', cluster_hadoop_lib_native],
            ['HADOOP_OPTS',
                "'\"${HADOOP_OPTS} -Djava.library.path=%s\"'" % (cluster_hadoop_lib_native)],
            ['HADOOP_CONF_DIR', cluster_hadoop_conf_dir],
            ['HADOOP_LOG_DIR', cluster_log_dir],                 # custom
            ['HADOOP_ROOT_LOGGER', 'DEBUG,console,RFA'],         # DEBUG mode custom
            ['HADOOP_DAEMON_ROOT_LOGGER', 'DEBUG,console,RFA'],  # DEBUG mode custom
            ['HADOOP_SECURITY_LOGGER', 'DEBUG,console,RFA'],     # DEBUG mode custom
            # ['YARN_CONF_DIR', cluster_hadoop_conf_dir],        # Deprecated
            # ['YARN_ROOT_LOGGER', 'DEBUG,console,RFA'],         # Deprecated
        ]

        ins = " && ".join(map(lambda x:
                              "put_config_line --file %s --property %s --value %s --prefix 'export' " %
                              (hadoop_env_file, x[0], x[1]), envlist))

        retcode = Command.do(ins)

        logger.info("ins: %s; retcode: %d." % (ins, retcode))

        if retcode != 0:
            logger.error(ins)
            return False

        #
        # configure ./etc/hadoop/hadoop-metrics2.properties
        #
        shutil.copy2('./configs/default/hadoop-metrics2.properties',
                     './configs/hadoop-metrics2.properties')
        hadoop_metrics_file = './configs/hadoop-metrics2.properties'
        gmond_host = self.ys['gmond']['host']

        envlist = [
                # ['jobhistoryserver.sink.ganglia.servers', gmond_host],
                # ['mrappmaster.sink.ganglia.servers', gmond_host],
                ['nodemanager.sink.ganglia.servers', gmond_host],
                ['resourcemanager.sink.ganglia.servers', gmond_host],
                # ['datanode.sink.ganglia.servers', gmond_host],
                # ['namenode.sink.ganglia.servers', gmond_host],
                # ['datanode.sink.file.filename', 'datanode-metrics.out'],
                ['resourcemanager.sink.file.filename', 'resourcemanager-metrics.out'],
                ['nodemanager.sink.file.filename', 'nodemanager-metrics.out'],
                # ['mrappmaster.sink.file.filename', 'mrappmaster-metrics.out'],
                # ['jobhistoryserver.sink.file.filename', 'jobhistoryserver-metrics.out'],
                ['nodemanager.sink.file_jvm.class', 'org.apache.hadoop.metrics2.sink.FileSink'],
                ['nodemanager.sink.file_jvm.context', 'jvm'],
                ['nodemanager.sink.file_jvm.filename', 'nodemanager-jvm-metrics.out'],
                ['nodemanager.sink.file_mapred.class', 'org.apache.hadoop.metrics2.sink.FileSink'],
                ['nodemanager.sink.file_mapred.context', 'mapred'],
                ['nodemanager.sink.file_mapred.filename', 'nodemanager-mapred-metrics.out'],
                ['*.sink.ganglia.class', 'org.apache.hadoop.metrics2.sink.ganglia.GangliaSink31'],
                ['*.sink.ganglia.period', '10'],
                ['*.sink.ganglia.supportsparse', 'true'],
                ['*.sink.ganglia.slope', 'jvm.metrics.gcCount=zero,jvm.metrics.memHeapUsedM=both'],
                ['*.sink.ganglia.dmax', 'jvm.metrics.threadsBlocked=70,jvm.metrics.memHeapUsedM=40'],
        ]

        ins = " && ".join(map(lambda x:
                              "put_config_line --file %s --property %s --value %s " %
                              (hadoop_metrics_file, x[0], x[1]), envlist))

        retcode = Command.do(ins)

        logger.info("ins: %s; retcode: %d." % (ins, retcode))

        if retcode != 0:
            logger.error(ins)
            return False

        #
        # sync configures
        #
        host_list = self.getHosts()
        rm_list = self.getHosts(roles=['resourcem', ])

        """ chmod """
        instructions = list()
        for host in host_list:
            ins = "ssh {0} {2}@{1} -tt 'sudo -S chmod -R 777 {3}' ".format(
                ssh_option, host['ip'], host['usr'], cluster_hadoop_conf_dir)

            instructions.append((ins, host['pwd']))

        ret = Command.parallel(instructions)
        if not ret:
            return ret

        """ sync files to all nodes """
        hbe_configs = './configs/hdfs-site.xml ./configs/mapred-site.xml \
                           ./configs/yarn-site.xml ./configs/core-site.xml \
                           ./configs/workers ./configs/hadoop-env.sh \
                           ./configs/hadoop-metrics2.properties'

        instructions = list()
        for host in host_list:
            ins = "ssh {1}@{0} -tt 'mkdir -p {3}' && scp {2} {1}@{0}:{3} ".format(
                host['ip'], host['usr'],
                hbe_configs, cluster_hadoop_conf_dir)

            instructions.append(ins)

        ret = Command.parallel(instructions)
        if not ret:
            return ret

        """ sync files to RMs """
        instructions = list()
        for host in rm_list:
            ins = "ssh {1}@{0} -tt 'mkdir -p {3}' && scp ./configs/yarn-rm-site.xml {1}@{0}:{2}".format(
                host['ip'], host['usr'],
                os.path.join(cluster_hadoop_conf_dir, 'yarn-site.xml'),
                cluster_hadoop_conf_dir)

            instructions.append(ins)

        return Command.parallel(instructions)


def trigger(ys):
    e = Custom(ys, attempts=3, interval=3, auto=True)
    return e.status
