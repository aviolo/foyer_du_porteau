#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Script to control fdp server.

Usage: <script name> [-d] [start|restart|stop|dump|update]
    -d: daemonize
'''
import datetime
import imp
import os
import subprocess
import sys
# Django web utils
from django_web_utils.daemon.daemonization import daemonize
from django_web_utils import system_utils

USER = 'fdp'
BASE_DIR = '/home/fdp/fdp'
TEMP_DIR = '%s/temp' % BASE_DIR
CONF_OVERRIDE = '%s/settings_override.py' % BASE_DIR
DUMPS_DIR = '%s/dbdumps' % BASE_DIR
LOG_PATH = '%s/startup.log' % TEMP_DIR
UWSGI_PID = '%s/uwsgi.pid' % TEMP_DIR
USWGI_INI = '%s/scripts/uwsgi.ini' % BASE_DIR


def _log(text=''):
    print(text, file=sys.stdout)
    sys.stdout.flush()


def _err(text=''):
    print(text, file=sys.stderr)
    sys.stderr.flush()


def _exec(*args):
    _log('>>> %s' % ' '.join(args))
    shell = len(args) == 1
    p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr, shell=shell)
    p.communicate()
    sys.stdout.flush()
    sys.stderr.flush()
    return p.returncode


if __name__ == '__main__':
    now = datetime.datetime.now()
    # Check that the script is not running
    _log('Checking that the script is not currently running...')
    rc = _exec('ps aux | grep -v grep | grep -v " %s " | grep -v " %s " | grep "%s"' % (os.getpid(), os.getppid(), __file__))
    if rc == 0:
        _err('The script is already running.')
        sys.exit(1)
    _log('OK')
    # Get command
    args = list(sys.argv)
    if '-d' in args:
        should_daemonize = True
        args.remove('-d')
    else:
        should_daemonize = False
    action = args[1] if len(args) > 1 else None
    actions = ('start', 'restart', 'stop', 'dump', 'update')
    if action not in actions:
        _err('Invalid action requested. Possible actions are %s.' % ', '.join(actions))
        sys.exit(1)
    # Check user
    user_name = os.environ['USER']
    if os.environ['USER'] != USER:
        system_utils.run_as(USER)
    # Daemonize
    if should_daemonize:
        wd = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        daemonize(redirect_to=LOG_PATH, rundir=wd)
        sys.path.append(wd)
    # Write initial info in log
    _log('Started on %s by user %s.' % (now.strftime('%Y-%m-%d %H:%M:%S'), user_name))
    # Dump db
    if action in ('dump', 'update'):
        _log('\n---- Dumping database ----')
        db_path = '%s/db.sqlite3' % BASE_DIR
        dump_cmd = None
        if os.path.exists(CONF_OVERRIDE):
            conf = imp.load_source('conf', CONF_OVERRIDE)
            if hasattr(conf, 'DATABASES') and conf.DATABASES.get('default'):
                dbs = conf.DATABASES.get('default')
                if 'sqlite' in dbs.get('ENGINE'):
                    if dbs.get('NAME'):
                        db_path = dbs.get('NAME')
                else:
                    # MySQL
                    dump_cmd = 'mysqldump -u %s %s %s --ignore-table=fdp.django_session > "%s/%s.sql"' % (
                        dbs.get('USER', 'root'),
                        '-p"%s"' % dbs['PASSWORD'] if dbs.get('PASSWORD') else '',
                        dbs.get('NAME', 'fdp'),
                        DUMPS_DIR,
                        now.strftime('%Y-%m-%d_%H-%M-%S'),
                    )
        if not dump_cmd:
            dump_cmd = 'cp "%s" "%s/%s.db"' % (db_path, DUMPS_DIR, now.strftime('%Y-%m-%d_%H-%M-%S'))
        if not os.path.exists(DUMPS_DIR):
            os.makedirs(DUMPS_DIR)
        rc = _exec(dump_cmd)
        if rc != 0:
            sys.exit(rc)
    # Update
    if action == 'update':
        _log('\n---- Updating server ----')
        rc = _exec('cd %s && git pull' % BASE_DIR)
        if rc != 0:
            sys.exit(rc)
        action = 'restart'
    # Stop
    if action in ('start', 'restart', 'stop'):
        _log('\n---- Stopping server ----')
        rc = _exec('pkill', '-U', USER, '-9', '-f', '--', 'uwsgi --ini %s' % USWGI_INI)
        _log('pkill return code: %s' % rc)
        if action == 'stop':
            sys.exit(0)
    # Start
    if action in ('start', 'restart'):
        _log('\n---- Starting server ----')
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
        if 'UWSGI_ORIGINAL_PROC_NAME' in os.environ:
            del os.environ['UWSGI_ORIGINAL_PROC_NAME']
        if 'UWSGI_RELOADS' in os.environ:
            del os.environ['UWSGI_RELOADS']
        os.execl('/usr/bin/uwsgi', 'uwsgi', '--ini', '%s' % USWGI_INI)
