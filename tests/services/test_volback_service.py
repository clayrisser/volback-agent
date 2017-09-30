import unittest
from app.services import volback_service

Volback = volback_service.Volback

def main():
    unittest.main(module=__name__)

class TestVolbackService(unittest.TestCase):

    def setUp(self):
        self.repo = '/backup'
        self.volback = Volback(self.repo, passphrase=None, verbose=True)

    def test_volback_service(self):
        self.assertIsNotNone(volback_service)

    def test_backup(self):
        self.volback.backup(container_ids=['some-mongo'], mount_destinations=None)
        self.assertTrue(True)

if __name__ == '__main__':
    main()
