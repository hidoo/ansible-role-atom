#!/usr/bin/env python

import json
import unittest
from unittest.mock import patch
from test.support import captured_stdout
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible.module_utils.basic import AnsibleModule
from library.apm import ApmModule


def set_module_args(args):
    """
    prepare arguments so that they will be picked up during module creation
    """
    value = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(value)


class TestApmModule(unittest.TestCase):
    def test_is_package_installed(self):
        with patch.object(AnsibleModule, "run_command") as mocked_run_command:
            cases = [
                ("hoge", True),
                ("fuga", True),
                ("piyo", True),
                ("not_installed_package", False),
            ]
            mocked_run_command.return_value = (
                0,
                (
                    "piyo@0.0.0\n"
                    "fuga@0.0.0\n"
                    "hoge@0.0.0"
                ),
                ""
            )

            for case in cases:
                name, installed = case
                set_module_args({"name": name})
                apm = ApmModule()

                expected = (0, installed)
                actual = apm.is_package_installed(name)
                self.assertTupleEqual(expected, actual)

    def test_is_package_installed_when_fail(self):
        with patch.object(AnsibleModule, "run_command") as mocked_run_command:
            name = "hoge"
            mocked_run_command.return_value = (1, "", "error detail")
            set_module_args({"name": name})
            apm = ApmModule()

            expected = (1, False)
            actual = apm.is_package_installed(name)
            self.assertTupleEqual(expected, actual)

    def test_package_install_when_installed(self):
        with patch.object(
            ApmModule, "is_package_installed"
        ) as mocked_is_package_installed:
            name = "hoge"
            mocked_is_package_installed.return_value = (0, True)
            set_module_args({"name": name})
            apm = ApmModule()

            expected = (0, False)
            actual = apm.package_install(name)
            self.assertTupleEqual(expected, actual)

    def test_package_install_when_not_installed(self):
        with patch.object(AnsibleModule, "run_command") as mocked_run_command:
            with patch.object(
                ApmModule, "is_package_installed"
            ) as mocked_is_package_installed:
                name = "hoge"
                stdout = "Installing {0} to /path/to/.atom/packages ✓"
                mocked_run_command.return_value = (0, stdout.format(name), "")
                mocked_is_package_installed.return_value = (0, False)
                set_module_args({"name": name})
                apm = ApmModule()

                expected = (0, True)
                actual = apm.package_install(name)
                self.assertTupleEqual(expected, actual)

    def test_package_upgrade_when_latest_and_installed(self):
        with patch.object(
            ApmModule, "is_not_package_latest"
        ) as mocked_is_not_package_latest:
            with patch.object(
                ApmModule, "is_package_installed"
            ) as mocked_is_package_installed:
                mocked_is_not_package_latest.return_value = (0, False)
                mocked_is_package_installed.return_value = (0, True)

                name = "hoge"
                set_module_args({"name": name})
                apm = ApmModule()

                expected = (0, False)
                actual = apm.package_upgrade(name)
                self.assertTupleEqual(expected, actual)

    def test_package_upgrade_when_latest_and_not_installed(self):
        with patch.object(
            ApmModule, "is_not_package_latest"
        ) as mocked_is_not_package_latest:
            with patch.object(ApmModule, "package_install") as mocked_package_install:
                mocked_is_not_package_latest.return_value = (0, False)
                mocked_package_install.return_value = (0, True)

                name = "hoge"
                set_module_args({"name": name})
                apm = ApmModule()

                expected = (0, True)
                actual = apm.package_upgrade(name)
                self.assertTupleEqual(expected, actual)

    def test_package_upgrade_when_not_latest(self):
        with patch.object(
            ApmModule, "is_not_package_latest"
        ) as mocked_is_not_package_latest:
            with patch.object(AnsibleModule, "run_command") as mocked_run_command:
                name = "hoge"
                stdout = (
                    "Package Updates Available (1)\n"
                    "└── {0} 0.0.0 -> 0.0.1\n"
                    "\n"
                    "Installing {0}@0.0.1 to /path/to/.atom/packages ✓"
                )
                mocked_is_not_package_latest.return_value = (0, True)
                mocked_run_command.return_value = (0, stdout.format(name), "")
                set_module_args({"name": name})
                apm = ApmModule()

                expected = (0, True)
                actual = apm.package_upgrade(name)
                self.assertTupleEqual(expected, actual)

    def test_package_uninstall_when_installed(self):
        with patch.object(AnsibleModule, "run_command") as mocked_run_command:
            with patch.object(
                ApmModule, "is_package_installed"
            ) as mocked_is_package_installed:
                name = "hoge"
                stdout = "Uninstalling {0} ✓"
                mocked_run_command.return_value = (0, stdout.format(name), "")
                mocked_is_package_installed.return_value = (0, True)
                set_module_args({"name": name})
                apm = ApmModule()

                expected = (0, True)
                actual = apm.package_uninstall(name)
                self.assertTupleEqual(expected, actual)

    def test_package_uninstall_when_not_installed(self):
        with patch.object(
            ApmModule, "is_package_installed"
        ) as mocked_is_package_installed:
            name = "hoge"
            mocked_is_package_installed.return_value = (0, False)
            set_module_args({"name": name})
            apm = ApmModule()

            expected = (0, False)
            actual = apm.package_uninstall(name)
            self.assertTupleEqual(expected, actual)

    def test_main_when_state_present_and_changed(self):
        with captured_stdout() as stdout:
            with patch.object(ApmModule, "package_install") as mocked_package_install:
                mocked_package_install.return_value = (0, True)
                name = "hoge"

                try:
                    set_module_args({"name": name, "state": "present"})
                    apm = ApmModule()
                    apm.main()
                except SystemExit:
                    actual = json.loads(stdout.getvalue())
                    mocked_package_install.assert_called_with(name)
                    self.assertEqual(True, actual["changed"])
                    self.assertEqual(0, actual["rc"])
                    self.assertEqual(apm.stderr, actual["stderr"])
                    self.assertEqual(apm.stdout, actual["stdout"])

    def test_main_when_state_present_and_not_changed(self):
        with captured_stdout() as stdout:
            with patch.object(ApmModule, "package_install") as mocked_package_install:
                mocked_package_install.return_value = (0, False)
                name = "hoge"

                try:
                    set_module_args({"name": name, "state": "present"})
                    apm = ApmModule()
                    apm.main()
                except SystemExit:
                    actual = json.loads(stdout.getvalue())
                    mocked_package_install.assert_called_with(name)
                    self.assertEqual(False, actual["changed"])
                    self.assertEqual(0, actual["rc"])
                    self.assertEqual(apm.stderr, actual["stderr"])
                    self.assertEqual(apm.stdout, actual["stdout"])

    def test_main_when_state_latest_and_changed(self):
        with captured_stdout() as stdout:
            with patch.object(ApmModule, "package_upgrade") as mocked_package_upgrade:
                mocked_package_upgrade.return_value = (0, True)
                name = "hoge"

                try:
                    set_module_args({"name": name, "state": "latest"})
                    apm = ApmModule()
                    apm.main()
                except SystemExit:
                    actual = json.loads(stdout.getvalue())
                    mocked_package_upgrade.assert_called_with(name)
                    self.assertEqual(True, actual["changed"])
                    self.assertEqual(0, actual["rc"])
                    self.assertEqual(apm.stderr, actual["stderr"])
                    self.assertEqual(apm.stdout, actual["stdout"])

    def test_main_when_state_latest_and_not_changed(self):
        with captured_stdout() as stdout:
            with patch.object(ApmModule, "package_upgrade") as mocked_package_upgrade:
                mocked_package_upgrade.return_value = (0, False)
                name = "hoge"

                try:
                    set_module_args({"name": name, "state": "latest"})
                    apm = ApmModule()
                    apm.main()
                except SystemExit:
                    actual = json.loads(stdout.getvalue())
                    mocked_package_upgrade.assert_called_with(name)
                    self.assertEqual(False, actual["changed"])
                    self.assertEqual(0, actual["rc"])
                    self.assertEqual(apm.stderr, actual["stderr"])
                    self.assertEqual(apm.stdout, actual["stdout"])

    def test_main_when_state_absent_and_changed(self):
        with captured_stdout() as stdout:
            with patch.object(
                ApmModule, "package_uninstall"
            ) as mocked_package_uninstall:
                mocked_package_uninstall.return_value = (0, True)
                name = "hoge"

                try:
                    set_module_args({"name": name, "state": "absent"})
                    apm = ApmModule()
                    apm.main()
                except SystemExit:
                    actual = json.loads(stdout.getvalue())
                    mocked_package_uninstall.assert_called_with(name)
                    self.assertEqual(True, actual["changed"])
                    self.assertEqual(0, actual["rc"])
                    self.assertEqual(apm.stderr, actual["stderr"])
                    self.assertEqual(apm.stdout, actual["stdout"])

    def test_main_when_state_absent_and_not_changed(self):
        with captured_stdout() as stdout:
            with patch.object(
                ApmModule, "package_uninstall"
            ) as mocked_package_uninstall:
                mocked_package_uninstall.return_value = (0, False)
                name = "hoge"

                try:
                    set_module_args({"name": name, "state": "absent"})
                    apm = ApmModule()
                    apm.main()
                except SystemExit:
                    actual = json.loads(stdout.getvalue())
                    mocked_package_uninstall.assert_called_with(name)
                    self.assertEqual(False, actual["changed"])
                    self.assertEqual(0, actual["rc"])
                    self.assertEqual(apm.stderr, actual["stderr"])
                    self.assertEqual(apm.stdout, actual["stdout"])

    def test_run_when_name_not_set(self):
        with captured_stdout() as stdout:

            try:
                set_module_args({})
                ApmModule()
            except SystemExit:
                actual = json.loads(stdout.getvalue())
                self.assertEqual(True, actual["failed"])


if __name__ == "__main__":
    unittest.main()
