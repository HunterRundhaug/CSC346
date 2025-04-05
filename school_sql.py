#!/usr/bin/env python3

import cgi
import os
import sys

path = os.environ.get('PATH_INFO', '')
method = os.environ.get('REQUEST_METHOD', '')

def main():
    pathSplit = path.split('/')

    if len(pathSplit) < 1:
        invalidRequest()
        return

    if(pathSplit[0] == "students"): # a request regarding students

        if(method == "GET"): # get students
            print("Status: 200")
            print("Content-Type: text/plain")
            print()
            print(" GET STUDENTS ")
            pass

        elif method == "POST": # post students ??
            pass
        
    elif pathSplit[0] == "course": # a request regarding courses
        
        pass

    else:
        invalidRequest();



def invalidRequest():
    print("Status: 400 Bad Request")
    print("Content-Type: text/plain")
    print()
    print("no path provided")


main()
