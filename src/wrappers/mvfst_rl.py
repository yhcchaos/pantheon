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
    cmd = '{} --inference'.format(path.join(cc_repo, 'setup.sh'))
    check_call(cmd, shell=True, cwd=path.join(cc_repo))

def dependencies_mvfst():
    # We use unzip and wget when installing torch
    our_dependencies = "unzip wget"

    # This is the list in https://github.com/facebookincubator/mvfst/blob/master/build_helper.sh
    linux_mvfst_dependencies = " ".join([
        "g++",
        "cmake",
        "libboost-all-dev",
        "libevent-dev",
        "libdouble-conversion-dev",
        "libgoogle-glog-dev",
        "libgflags-dev",
        "libiberty-dev",
        "liblz4-dev",
        "liblzma-dev",
        "libsnappy-dev",
        "make",
        "zlib1g-dev",
        "binutils-dev",
        "libjemalloc-dev",
        "libssl-dev",
        "pkg-config",
        "libsodium-dev",
        ])
    print("{} {}".format(our_dependencies, linux_mvfst_dependencies))

def get_test_cc_env_args(cc_repo):
    model_file = path.join(cc_repo, 'models', 'traced_model.pt')
    flags_file = path.join(cc_repo, 'models', 'traced_model.flags.pkl')

    cc_env_args = []
    if path.exists(model_file):
        cc_env_args = ['--cc_env_model_file={}'.format(model_file)]

    if path.exists(flags_file):
        with open(flags_file, 'rb') as f:
            obj = pkl.load(f)
            assert isinstance(obj, dict)

            # Override to local mode for testing
            obj['cc_env_mode'] = 'local'

            for k, v in obj.iteritems():
                if k.startswith('cc_env'):
                    cc_env_args.append('--{}={}'.format(k, v))

    return cc_env_args


def main():
    args = arg_parser.sender_first()

    cc_repo = path.join(context.third_party_dir, 'mvfst-rl')
    src = path.join(cc_repo, '_build/build/traffic_gen/traffic_gen')

    if args.option == 'deps':
        dependencies_mvfst()
        return

    if args.option == 'setup':
        setup_mvfst(cc_repo)
        return

    if args.option == 'sender':
        # If --extra_args is set, then we are in train mode.
        # Otherwise, load flags from pkl file.
        if args.extra_args:
            cc_env_args = args.extra_args.split()
        else:
            cc_env_args = get_test_cc_env_args(cc_repo)

        cmd = [
            src,
            '--mode=server',
            '--host=0.0.0.0',  # Server listens on 0.0.0.0
            '--port=%s' % args.port,
            '--cc_algo=rl',
        ] + cc_env_args
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
