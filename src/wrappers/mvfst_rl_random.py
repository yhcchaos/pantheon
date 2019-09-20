#!/usr/bin/env python2

# Random RL policy

import os
from os import path
import sys
import string
import shutil
import time
from subprocess import check_call, call, Popen, PIPE

import arg_parser
import context
from helpers import utils


def setup_mvfst(cc_repo):
    cmd = '{} --inference'.format(path.join(cc_repo, 'setup.sh'))
    check_call(cmd, shell=True, cwd=path.join(cc_repo))


def main():
    args = arg_parser.sender_first()

    cc_repo = path.join(context.third_party_dir, 'mvfst-rl')
    src = path.join(cc_repo, '_build/build/traffic_gen/traffic_gen')

    if args.option == 'setup':
        setup_mvfst(cc_repo)
        return

    if args.option == 'sender':
        cmd = [
            src,
            '--mode=server',
            '--host=0.0.0.0',  # Server listens on 0.0.0.0
            '--port=%s' % args.port,
            '--cc_algo=rl',
        ] + args.extra_args.split() + [
            # extra_args might have --cc_env_mode already, so we set this
            # at the end to override.
            '--cc_env_mode=random',
        ]
        check_call(cmd)
        return

    # We use cubic for the client side to keep things simple. It doesn't matter
    # here as we are simulating server-to-client flow, and the client simply
    # sends a hello message to kick things off.
    if args.option == 'receiver':
        cmd = [
            src,
            '--mode=client',
            '--host=%s' % args.ip,
            '--port=%s' % args.port,
            '--cc_algo=cubic',
        ]
        check_call(cmd)
        return


if __name__ == '__main__':
    main()
