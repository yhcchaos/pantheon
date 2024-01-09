#!/usr/bin/env python2

from os import path
from subprocess import check_call

import arg_parser
import context
from helpers import kernel_ctl

def setup_dbbr():
    kernel_ctl.load_kernel_module('tcp_bbr')
    kernel_ctl.enable_congestion_control('bbr')


def main():
    args = arg_parser.sender_first()
    cc_repo = path.join(context.third_party_dir, 'deeptcp')
    ddpg_src = path.join(cc_repo, 'rl-module')
    send_src = path.join(cc_repo, 'server.sh')
    recv_src = path.join(cc_repo, 'client.sh')

    if args.option == 'setup':
        setup_dbbr()
        sh_cmd = './build.sh'
        check_call(sh_cmd, shell=True, cwd=cc_repo)
        return

    if args.option == 'setup_after_reboot':
        setup_dbbr()
        return

    if args.option == 'sender':
        cmd = [send_src, args.port, ' 50',' 150',' 20',' 2', 'bbr ', ddpg_src]
        check_call(cmd)
        return

    if args.option == 'receiver':
        cmd = [recv_src, args.ip, ' 1 ' ,args.port, ddpg_src]
        check_call(cmd)
        return

if __name__ == '__main__':
    main()
