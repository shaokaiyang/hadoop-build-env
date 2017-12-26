#!/usr/bin/env python3

# Copyright 2017 by xiaoyang.xshaun. All Rights Reserved.
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Vinay Sajip
# not be used in advertising or publicity pertaining to distribution
# of the software without specific, written prior permission.
# VINAY SAJIP DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# VINAY SAJIP BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""
WELCOME YOUR EMAILS ABOUT COMMUNICATION AND CONSULTATION 
AUTHOR: XIAOYANG SUN (xshaun@outlook.com).ALL RIGHTS RESERVED
"""

import os
import sys
import yaml
import logging
import logging.config

#---------------------------------------------------------------------------
#   Definitions
#---------------------------------------------------------------------------

#
# _logging_config is used to configue logging
# _logging_logger is used to get a logger
#
_logging_config = './configs/logging.config'
_logging_logger = 'develop'

#
# _settings_file indicates where is
#
_settings_file = './settings.yaml'


#---------------------------------------------------------------------------
#   Core Logic
#---------------------------------------------------------------------------

logging.config.fileConfig(_logging_config)
logger = logging.getLogger(_logging_logger)


def _parse_yaml_settings(abspath_filename):
    ys = None

    try:
        if not os.path.isfile(abspath_filename):
            raise Exception('not found the setting file.')

        file = open(abspath_filename)
        ys = yaml.load(file)  # setting file with yaml format

        """
        @annotation:
            to detect necessary fields within setting file.
            to judge whether each field value is legal.
        """

        # checker
        for item in ('mode', 'sourcecode', 'binarycode', 'roles', 'steps', 'stages'):
            if item not in ys:
                raise Exception(
                    "not found field '%s' in setting file." % (item))

        # checker
        if ys['mode'] not in ('pseudo-distributed', 'fully-distributed'):
            raise Exception("ys['mode'] has an illegal value in setting file.")

        # checker
        if ys['mode'] == 'pseudo-distributed' and (
                len(ys['roles']['resourcem']['hosts']) != 1 or
                ys['roles']['resourcem'] != ys['roles']['nodem']):
            raise Exception(
                'rm and nms must only have one, and same value under pseudo-distributed mode in setting file.')

        return ys

    except Exception as e:
        logger.error(
            "catched exceptions while loading setting file: %s" % (str(e)))
        ys = None

    finally:
        return ys


def main(stage=None, params=list()):
    ys = _parse_yaml_settings(os.path.abspath(_settings_file))
    if ys is None:
        return 1

    ys['params'] = params

    if stage not in ys['stages']:
        logger.error('defined stage is not in settings.yaml')
        return 1

    try:
        for step in ys['stages'][stage]:
            obj = __import__("scripts.%s" % (ys['steps'][step]), fromlist=True)
            func = getattr(obj, 'trigger')
            if not func(ys):
                raise Exception("errors occurs in scripts.%s" %
                                (ys['steps'][step]))

    except Exception as e:
        logger.error(str(e))
        return 1

    return 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        logger.error('Missing the necessary stage parameter')
        exit()

    retcode = main(stage=sys.argv[1], params=sys.argv[2:])
    if retcode != 0:
        print("stage '%s' failed" % (sys.argv[i]))
        exit()
