import unittest2 as unittest
from rds_log_dog.rds_instance import RDSInstance


class Test(unittest.TestCase):

    def test_constructor(self):
        rds = RDSInstance('foo')
        self.assertEqual('foo', rds.name)
        self.assertEqual('mysql', rds.engine)

    def test_engine(self):
        rds = RDSInstance('foo', engine='engine')
        self.assertEqual('foo', rds.name)
        self.assertEqual('engine', rds.engine)
