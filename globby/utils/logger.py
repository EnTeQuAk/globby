#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
    globby.utils.logger
    ~~~~~~~~~~~~~~~~~~~

    Provides the logging functionality for Globby.

    :copyright: 2006-2007 by Christopher Grebs.
    :license: GNU GPL, see LICENSE for more details.
"""

import os, re
from os.path import join, exists
from datetime import datetime

from globby.cli.colors import bold


class Logger:
    """
    Give us the var ``self.logger`` to post log messages.
    """
    def __init__(self, logs_path, debug=False, timeformat='%H:%M:%S'):
        self.logs_path = logs_path
        self.debug = debug
        self._timeformat = timeformat
        self.date = datetime.now()
        if not exists(self.logs_path):
            os.mkdir(self.logs_path)
        log_file_name = join(
            self.logs_path,
            '%d-%d-%d_[%d-%d-%d].log' % (
                self.date.year, self.date.month,
                self.date.day, self.date.hour,
                self.date.minute, self.date.second
            )
        )
        if exists(log_file_name):
            self.log_file = open(log_file_name, 'a')
        else:
            self.log_file = open(log_file_name, 'w')

        # clean 'logs' directory
        self.clean_logs()

    def clean_logs(self):
        """
        Count existing log files.
        If more then 50 log files exist Globby will delete them all
        """
        log_re = re.compile(
            r'\d{4}-\d{1,2}-\d{1,2}_\[(?:\d{1,2}-){2}\d{1,2}\].log'
        )
        log_counter = 0
        for log in os.listdir(self.logs_path):
            if log_re.match(log):
                log_counter += 1
        if log_counter > 50:
            self.info_msg(bold(_(
                'The maximum of log files is arrived.'
                ' I\'ll delete all logs!'
                ))
            )
            for log_file in os.listdir(self.logs_path):
                if os.path.isfile(join(self.logs_path, log_file)):
                    os.remove(join(self.logs_path, log_file))


    def debug_msg(self, msg):
        self._log(0, msg)

    def info_msg(self, msg):
        self._log(1, msg)

    def warn_msg(self, msg):
        self._log(2, msg)

    def error_msg(self, msg):
        self._log(3, msg)

    def _log(self, level, msg):
        time = self.date.strftime(self._timeformat)
        level_dict = {
            0: 'DEBUG',
            1: 'INFO',
            2: 'WARNING',
            3: 'ERROR',
        }
        _level = level_dict.get(level)
        output = '%s[%s]\n    %s\n' % (_level, time, msg)
        if level in level_dict.keys():
            if not (level == 0 and not self.debug):
                print output
        self.log_file.write(output)
