#!/usr/bin/env python

from ansible.module_utils.basic import AnsibleModule


class ApmModule:
    def __init__(self):
        self.module = AnsibleModule(
            argument_spec={
                "name": {"type": "str", "required": True},
                "state": {
                    "choices": ["latest", "present", "absent"],
                    "default": "present",
                },
            },
            supports_check_mode=True,
        )
        self.stdout = ""
        self.stderr = ""

    def is_package_installed(self, name):
        rc, stdout, stderr, installed = (0, "", "", False)
        command = "apm list --bare --color=false"
        rc, stdout, stderr = self.module.run_command(command)

        if rc == 0 and stdout.find(name + "@") >= 0:
            installed = True

        self.stdout, self.stderr = stdout, stderr
        return (rc, installed)

    def is_not_package_latest(self, name):
        rc, stdout, stderr, not_latest = (0, "", "", False)
        command = "apm upgrade --list --color=false"
        rc, stdout, stderr = self.module.run_command(command)

        if rc == 0 and stdout.find(" " + name + " ") >= 0:
            not_latest = True

        self.stdout, self.stderr = stdout, stderr
        return (rc, not_latest)

    def package_install(self, name):
        rc, stdout, stderr, changed = (0, "", "", False)
        command = "apm install {0} --color=false".format(name)
        rc, installed = self.is_package_installed(name)

        if rc == 0 and not installed:
            rc, stdout, stderr = self.module.run_command(command)
            changed = True

        self.stdout, self.stderr = stdout, stderr
        return (rc, changed)

    def package_upgrade(self, name):
        rc, stdout, stderr, changed = (0, "", "", False)
        command = "apm upgrade {0} --confirm=false".format(name)
        rc, not_latest = self.is_not_package_latest(name)

        if rc == 0:
            if not_latest:
                rc, stdout, stderr = self.module.run_command(command)
                self.stdout, self.stderr = stdout, stderr
                changed = True
            else:
                rc, changed = self.package_install(name)

        return (rc, changed)

    def package_uninstall(self, name):
        rc, stdout, stderr, changed = (0, "", "", False)
        command = "apm uninstall {0} --color=false".format(name)
        rc, installed = self.is_package_installed(name)

        if rc == 0 and installed:
            rc, stdout, stderr = self.module.run_command(command)
            changed = True

        self.stdout, self.stderr = stdout, stderr
        return (rc, changed)

    def main(self):
        rc, changed = (0, False)
        is_check_mode = self.module.check_mode

        # skip processing when check_mode is yes
        if is_check_mode:
            self.module.exit_json(changed=False)

        name = self.module.params["name"]
        state = self.module.params["state"]

        if state == "present":
            rc, changed = self.package_install(name)
        if state == "latest":
            rc, changed = self.package_upgrade(name)
        if state == "absent":
            rc, changed = self.package_uninstall(name)

        if rc == 0:
            self.module.exit_json(
                changed=changed, rc=rc, stdout=self.stdout, stderr=self.stderr
            )
        else:
            self.module.fail_json(
                msg="error", rc=rc, stdout=self.stdout, stderr=self.stderr
            )


if __name__ == "__main__":
    apm = ApmModule()
    apm.main()
