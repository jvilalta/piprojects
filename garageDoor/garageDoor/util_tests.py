import unittest
import util
class Test_util_tests(unittest.TestCase):
    def test_getEmailCommand(self):
        command = util.get_email_command()
        self.assertEquals("open",command)

if __name__ == '__main__':
    unittest.main()
