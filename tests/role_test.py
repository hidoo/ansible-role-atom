#!/usr/bin/env python

import re
import subprocess
import unittest
from subprocess import PIPE


def print_stdout(process):
    print("\n" + process.stdout.decode("utf8"))


def get_playbook_results(process):
    pattern = r"ok=(\d+)\s+changed=(\d+)\s+unreachable=(\d+)\s+failed=(\d+)"
    result = re.search(pattern, process.stdout.decode("utf8"))
    ok, changed, unreachable, failed = result.groups()
    return {
        "ok": ok,
        "changed": changed,
        "unreachable": unreachable,
        "failed": failed
    }


class TestAtomeRole(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        command = ["brew", "cask", "install", "atom"]
        process = subprocess.run(command, stdout=PIPE, stderr=PIPE)
        print_stdout(process)

    @classmethod
    def tearDownClass(self):
        try:
            command = ["apm", "uninstall", "zentabs"]
            process = subprocess.run(command, stdout=PIPE, stderr=PIPE)
            print_stdout(process)
        except SystemExit:
            pass

    def test_1_role_syntax(self):
        command = [
            "ansible-playbook",
            "-i",
            "./tests/inventory",
            "./tests/test.yml",
            "--syntax-check",
            "-vv"
        ]
        process = subprocess.run(command, stdout=PIPE, stderr=PIPE)
        print_stdout(process)
        self.assertEqual(0, process.returncode)

    def test_2_playbook_1_install_atom_when_skip_install(self):
        command = [
            "ansible-playbook",
            "-i",
            "./tests/inventory",
            "./tests/test.yml",
            "-t",
            "install_atom_when_skip_install",
            "-vv"
        ]
        process = subprocess.run(command, stdout=PIPE, stderr=PIPE)
        print_stdout(process)
        actual = get_playbook_results(process)
        expected = {
            "ok": "0",
            "changed": "0",
            "unreachable": "0",
            "failed": "0"
        }
        self.assertEqual(0, process.returncode)
        self.assertDictEqual(expected, actual)

    def test_2_playbook_2_package_install_when_not_installed(self):
        command = [
            "ansible-playbook",
            "-i",
            "./tests/inventory",
            "./tests/test.yml",
            "-t",
            "package_install_when_not_installed",
            "-vv"
        ]
        process = subprocess.run(command, stdout=PIPE, stderr=PIPE)
        print_stdout(process)
        actual = get_playbook_results(process)
        expected = {
            "ok": "1",
            "changed": "1",
            "unreachable": "0",
            "failed": "0"
        }
        self.assertEqual(0, process.returncode)
        self.assertDictEqual(expected, actual)

    def test_2_playbook_3_package_install_when_already_installed(self):
        command = [
            "ansible-playbook",
            "-i",
            "./tests/inventory",
            "./tests/test.yml",
            "-t",
            "package_install_when_already_installed",
            "-vv"
        ]
        process = subprocess.run(command, stdout=PIPE, stderr=PIPE)
        print_stdout(process)
        actual = get_playbook_results(process)
        expected = {
            "ok": "1",
            "changed": "0",
            "unreachable": "0",
            "failed": "0"
        }
        self.assertEqual(0, process.returncode)
        self.assertDictEqual(expected, actual)

    def test_2_playbook_4_package_uninstall_when_already_installed(self):
        command = [
            "ansible-playbook",
            "-i",
            "./tests/inventory",
            "./tests/test.yml",
            "-t",
            "package_uninstall_when_already_installed",
            "-vv"
        ]
        process = subprocess.run(command, stdout=PIPE, stderr=PIPE)
        print_stdout(process)
        actual = get_playbook_results(process)
        expected = {
            "ok": "1",
            "changed": "1",
            "unreachable": "0",
            "failed": "0"
        }
        self.assertEqual(0, process.returncode)
        self.assertDictEqual(expected, actual)

    def test_2_playbook_5_package_uninstall_when_already_uninstalled(self):
        command = [
            "ansible-playbook",
            "-i",
            "./tests/inventory",
            "./tests/test.yml",
            "-t",
            "package_uninstall_when_already_uninstalled",
            "-vv"
        ]
        process = subprocess.run(command, stdout=PIPE, stderr=PIPE)
        print_stdout(process)
        actual = get_playbook_results(process)
        expected = {
            "ok": "1",
            "changed": "0",
            "unreachable": "0",
            "failed": "0"
        }
        self.assertEqual(0, process.returncode)
        self.assertDictEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
