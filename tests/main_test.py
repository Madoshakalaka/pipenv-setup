import subprocess
import sys
import unittest


class MyTestCase(unittest.TestCase):
    def test_stuff(self):
        # todo: write tests
        pass

    def test_cmd(self):

        p = subprocess.Popen(
            [sys.executable, "-m", "pipenv_setup"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()

        out = out.decode(encoding="utf-8").strip()
        err = err.decode(encoding="utf-8").strip()

        # todo: tests for command line output
        self.assertTrue(out)
        self.assertFalse(err)

if __name__ == "__main__":
    unittest.main()
