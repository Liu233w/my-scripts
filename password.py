#!/usr/bin/env python3
import hashlib, os, getpass, sys

data = getpass.getpass(">>> ")
out = hashlib.new('md5', data.encode('utf-8'))

print(out.hexdigest())

print("Press enter to exit...", file=sys.stderr)
input()
