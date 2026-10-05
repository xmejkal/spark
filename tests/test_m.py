import sys, unittest
sys.path.insert(0, '.')
import m
class T(unittest.TestCase):
    def test_add(self): self.assertEqual(m.add(1, 2), 3)
