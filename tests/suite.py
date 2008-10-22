# -*- coding: utf-8 -*-
"""
    Globby unit tests
    ~~~~~~~~~~~~~~~~~

    How to build a new test
    =======================

     - create a new test file
     - import unittest
     - create your test suites (see below)

    Create you test suite
    ---------------------

     - a test suite must inherit from unittest.TestCase

     - add a function 'suite' that covers all unittests
       (see the example tests in the folder)

    :copyright: 2007 Christopher Grebs.
    :license: GNU GPL, see LICENSE for more details.
"""

import unittest


import test_environment as env
import test_markup as markup

def suite():
    test_suite = unittest.TestSuite()
    for suite in (env, markup):
        test_suite.addTest(suite.suite())
    return test_suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
