#!/venv/bin/python

import cgi
import os
import sys
import pyodbc
from db_config import DB_CONFIG

path = os.environ.get('PATH_INFO', '')
method = os.environ.get('REQUEST_METHOD', '')

def main():
    pathSplit = path.strip('/').split('/')

    if not pathSplit or pathSplit[0] == '':
        homePageRoute()
        return

    if(pathSplit[0] == "students"): # a request regarding students

        if(method == "GET" and len(pathSplit) < 2): # get students
            try:
                conn = connectToDB()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM students")
                rows = cursor.fetchall()

                students = ""
            except Exception as e:
                print("Status: 500 Internal Server Error")
                print("Content-Type: text/plain\n")
                print(f"Database error: {e}")

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students")
            rows = cursor.fetchall()
            students = ""
            for row in rows:
                 # row[0] is id, row[1] is name
                students += f"ID: {row[0]}, Name: {row[1]}\n"

            # CGI headers
            print("Status: 200 OK")
            print("Content-Type: text/plain\n")
            print(students)                  

        elif method == "POST": # post students ??
           invalidRequest()

        else:
           invalidRequest()
        
    elif pathSplit[0] == "course": # a request regarding courses
        
        pass

    else:
        invalidRequest();



def invalidRequest():
    print("Status: 400 Bad Request")
    print("Content-Type: text/plain")
    print()
    print(f'no path provided:{path}')

def homePageRoute():
    print("Status: 200 OK")
    print("Content-Type: text/plain")
    print()
    print("Welcome to the School API!")
    print("Here are the available endpoints:\n")
    print("GET /students                 - List all students")
    print("POST /students                - Add a new student")
    print("GET /students/<ID>            - Get a specific student by ID")
    print("PUT /students/<ID>            - Update a student's name")
    print("DELETE /students/<ID>         - Delete a student")
    print("POST /students/<ID>/courses   - Add a course to a student")
    print()
    print("GET /courses                  - List all courses")
    print("POST /courses                 - Add a new course")
    print("GET /courses/<ID>             - Get a specific course by ID")
    print("DELETE /courses/<ID>          - Delete a course")
    print()
    print("GET /debug                    - (Optional) Debug route to see all data")
    return

def connectToDB():
    conn = pyodbc.connect(
        f'DRIVER={DB_CONFIG["driver"]};'
        f'SERVER={DB_CONFIG["server"]};'
        f'DATABASE={DB_CONFIG["database"]};'
        f'UID={DB_CONFIG["username"]};'
        f'PWD={DB_CONFIG["password"]};'
        f'Encrypt={DB_CONFIG["encrypt"]};'
        f'TrustServerCertificate={DB_CONFIG["trust_cert"]};'
        f'Connection Timeout={DB_CONFIG["timeout"]};'
    )

    return conn


main()
