import signal
import sys


def handler(signum, frame):
    signame = signal.Signals(signum).name
    print(f'Received signal {signame} ({signum}), exiting...')
    sys.exit(0)


signal.signal(signal.SIGTERM, handler)
