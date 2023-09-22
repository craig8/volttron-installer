from subprocess import Popen, PIPE

import setup

setup.main()

Popen(['bash', '-c', 'python3 pages.py']).wait()
