#!/bin/bash
#
source ./utilities/functions.profile

# Recommend trusty (14.04LTS)

killall dpkg
killall apt-get
killall aptitude
dpkg --configure -a

# APT='apt-get'

# ----------------------------
# Installing required packages
#
# * Basic
apt-get -y install ssh pdsh curl expect libxml2-utils bats
# * Oracle JDK 1.8 (preferred)
apt-get -y purge openjdk*
add-apt-repository -y ppa:webupd8team/java
apt-get -y update
echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections
apt-get -y install oracle-java8-installer --allow-unauthenticated
apt-get -y install oracle-java8-set-default --allow-unauthenticated
apt-get -y install software-properties-common
# * Maven
apt-get -y install maven
# * Native libraries
apt-get -y install build-essential autoconf automake libtool cmake zlib1g-dev pkg-config libssl-dev
# * ProtocolBuffer 2.5.0 (required)
apt-get -y install libprotobuf-dev=2.5.0-9ubuntu1 protobuf-compiler=2.5.0-9ubuntu1
if [[ 0 != $? ]]; then
    if [[ ! -e /usr/bin/protoc || 'libprotoc 2.5.0' != `/usr/bin/protoc --version | grep 2.5.0`  ]]; then
        curl -sSL 'https://github.com/google/protobuf/releases/download/v2.5.0/protobuf-2.5.0.tar.gz' | tar -C /opt -xzv

        cd /opt/protobuf-2.5.0
        ./autogen.sh  &&  ./configure --prefix=/usr

        make  &&  make install && cp ./src/protoc /usr/bin/
        # protoc --version

        cd /opt/protobuf-2.5.0/java
        mvn install
    fi
fi

# ----------------------------
# Optional packages:
#
# * Snappy compression
apt-get -y install snappy libsnappy-dev
# * Bzip2
apt-get -y install bzip2 libbz2-dev
# * Jansson (C Library for JSON)
apt-get -y install libjansson-dev
# * Linux FUSE
apt-get -y install fuse libfuse-dev
# * ZStandard compression
apt-get -y install zstd
# * Findbugs (if running findbugs)
if [[ ! -d '/opt/findbugs-3.0.1' ]]; then
    curl -sSL 'https://jaist.dl.sourceforge.net/project/findbugs/findbugs/3.0.1/findbugs-noUpdateChecks-3.0.1.tar.gz' | tar -C '/opt' -xzv
fi

# ----------------------------
# Fix issues / Reset
#
# * pdsh set rsh to connect default,
#       reset ssh and reconnect terminal
#   -- pdsh -w localhost -l root uptime # test
put_config_line --file './utilities/user.profile' --property 'PDSH_RCMD_TYPE' --value 'ssh' --prefix 'export'

#
# * set findbugs home
put_config_line --file './utilities/user.profile' --property 'FINDBUGS_HOME' --value '/opt/findbugs-3.0.1' --prefix 'export'

#
# * set maven opts
put_config_line --file './utilities/user.profile' --property 'MAVEN_OPTS' --value '"-Xms512m -Xmx2048m"' --prefix 'export'
put_config_line --file './utilities/user.profile' --property 'JAVA_TOOL_OPTIONS' --value '"-Xms512m -Xmx2048m -XX:+UseConcMarkSweepGC -XX:-UseGCOverheadLimit"' --prefix 'export'
put_config_line --file './utilities/user.profile' --property 'JAVA_OPTS' --value '"-Xms512m -Xmx4096m"' --prefix 'export'

# ----------------------------
# Clean and Upgrade libs:
# apt-get -y upgrade
# apt-get -y autoremove
# apt-get -y autoclean

