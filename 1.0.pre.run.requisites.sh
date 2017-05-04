#!/bin/bash
#
source 0.*

# Recommend trusty (14.04LTS)

# APT='apt-get'

# ----------------------------
# Installing required packages
#
# * Basic
apt-get -y install ssh pdsh curl expect libxml2-utils
# * Oracle JDK 1.8 (preferred)
apt-get -y purge openjdk*
add-apt-repository -y ppa:webupd8team/java
apt-get -y update
echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections
apt-get -y install oracle-java8-installer --allow-unauthenticated
apt-get -y install oracle-java8-set-default --allow-unauthenticated
apt-get -y install software-properties-common

# ----------------------------
# Clean and Upgrade libs:
apt-get -y upgrade
apt-get -y autoremove
apt-get -y autoclean

