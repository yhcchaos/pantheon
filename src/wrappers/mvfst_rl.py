#!/usr/bin/env python2

import cPickle as pkl
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
    cmd = [path.join(cc_repo, 'setup.sh'), '--inference']
    check_call(cmd, shell=True, cwd=path.join(cc_repo))


def main():
    args = arg_parser.sender_first()

    cc_repo = path.join(context.third_party_dir, 'mvfst-rl')
    src = path.join(cc_repo, '_build/build/traffic_gen/traffic_gen')

    if args.option == 'setup':
        setup_mvfst(cc_repo)
        return

    if args.option == 'sender':
        directory = path.join(cc_repo, 'models')
        cc_env_args = [
            '--cc_env_model_file=%s' % path.join(directory, "traced_model.pt"),
        ]
        with open(path.join(directory, 'traced_model.flags.pkl'), "rb") as f:
            obj = pkl.load(f)
            assert isinstance(obj, dict)
            for k, v in obj.iteritems():
                if k.startswith("cc_env"):
                    option = "--{}={}".format(k, v)
                    cc_env_args.append(option)
        cmd = [
            src,
            '--mode=server',
            '--host=0.0.0.0',  # Server listens on 0.0.0.0
            '--port=%s' % args.port,
            '--cc_algo=rl',
        ] + args.extra_args.split() + cc_env_args
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
        ] + args.extra_args.split()
        check_call(cmd)
        return


if __name__ == '__main__':
    main()

