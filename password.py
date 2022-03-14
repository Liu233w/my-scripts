#!/usr/bin/env python3
import hashlib, os, getpass

data = getpass.getpass(">>> ")
out = hashlib.new('md5', data.encode('utf-8'))

print(out.hexdigest())

input("Press enter to exit...")
