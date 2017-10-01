import unittest
from app.__main__ import create_app

TestCase = unittest.TestCase

class TestMain(TestCase):

    def setUp(self):
        self.app = create_app()

    def test_main(self):
        self.assertIsNotNone(self.app)
        self.app.run()

def main():
    unittest.main(module=__name__, exit=False)

if __name__ == '__main__':
    main()
