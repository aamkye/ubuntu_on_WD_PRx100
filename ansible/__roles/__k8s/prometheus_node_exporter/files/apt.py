#!/usr/bin/env python3

import re
import subprocess
import os.path

class apt_upgrade_pending():
    def __init__(self):
        self.apt_list_re = re.compile(r'^(.+)\/([\w\-\,]+)\s(.+)\s([\w\d]+)(\s\[.+\:\s(.+)\])?$')
        self.non_proccessable = 0
        self.get_apt_upgradable_list()
        self.check_if_reboot_needed()
        self.print_non_proccessable()

    def get_apt_upgradable_list(self):
        p = subprocess.Popen(["apt", "list", "--upgradable"], stdout=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        print('# HELP node_apt_return_status APT return code.')
        print('# TYPE node_apt_return_status gauge')
        print('node_apt_return_status 0')
        print("")

        if p.returncode != 0:
            print(f'node_apt_return_status {p.returncode}')
            exit(0)

        print('# HELP node_apt_upgrade_pending Apt package pending updates by origin.')
        print('# TYPE node_apt_upgrade_pending gauge')
        for line in stdout.splitlines()[1:]:
            m = re.search(self.apt_list_re, line.decode("utf-8"))
            if not m:
                self.non_proccessable += 1
            else:
                m2 = re.search('security', m.group(4))
                print('node_apt_upgrade_pending{{package_name="{0}",new_version="{1}",origin="{2}",arch="{3}",security="{4}"}} 1'.format(m.group(1), m.group(3), m.group(2), m.group(4), "true" if m2 else "false" ))
        if len(stdout) == 0:
            print('node_apt_upgrade_pending{{package_name="",new_version="",origin="",arch="", security=""}} 0')
        print("")

    def check_if_reboot_needed(self):
        print('# HELP node_reboot_required Node reboot is required for software updates.')
        print('# TYPE node_reboot_required gauge')

        if os.path.isfile('/run/reboot-required'):
            print('node_reboot_required 1')
        else:
            print('node_reboot_required 0')
        print("")

    def print_non_proccessable(self):
        print('# HELP node_apt_upgrade_non_processable Not procesable lines.')
        print('# TYPE node_apt_upgrade_non_processable gauge')
        print(f'node_apt_upgrade_non_processable {self.non_proccessable}')
        print("")

def main():
    apt_upgrade_pending()

if __name__ == '__main__':
    main()
