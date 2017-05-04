# -*- coding: utf-8 -*-
import unittest


class Testloading(unittest.TestCase):

    def test_import(self):
        """ test_import """
        import clarindspace
        print clarindspace.__version__

if __name__ == '__main__':
    unittest.main()
