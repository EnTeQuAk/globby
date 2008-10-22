#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
    unittests for the Globby Environment
    ====================================

    :copyright: 2007 by Christopher Grebs
    :license: GNU GPL, see LICENSE for more details.
"""

import unittest
from os.path import dirname, abspath, join

from globby.environment import ProjectEnvironment, Environment


class EnvironmentTest(unittest.TestCase):

    def setUp(self):
        self.project_env = ProjectEnvironment(
            join(abspath(dirname(__name__)), 'tests'),
            'test-project1',
            'test-projects'
        )

    def test_project_env(self):
        self.assertEqual(self.project_env.all_projects, ['test-project1', 'test-project2'])
        self.assertEqual(self.project_env.all_files, ['test_file1'])
        self.assertEqual(self.project_env.all_files_unfiltered, ['test_file1.txt', 'menue.txt'])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EnvironmentTest, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main()
