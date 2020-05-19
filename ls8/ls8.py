#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *


if len(sys.argv) != 2:
    print("Need proper file name passed")
    sys.exit(1)

filename = sys.argv[1]
with open(filename) as program:
    cpu = CPU()
    cpu.load(program)
    cpu.run()