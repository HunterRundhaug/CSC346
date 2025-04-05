#!/usr/bin/env python3

import cgi
import os
import sys

path = os.environ.get('PATH_INFO', '')
method = os.environ.get('REQUEST_METHOD', '')

pathSplit = path.split('/')

splitstring = ""
for chunk in pathSplit:
    splitstring += chunk + " "
splitstring += method

print("Status: 200");
print("Content-Type: text/plain")
print()
print(" this is the body of the response")
print(splitstring)


