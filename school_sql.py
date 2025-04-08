#!/bin/python3

import json
import cgi
import os
import sys
import pyodbc
from db_config import DB_CONFIG
from server_config import Server_Info

import cgitb
cgitb.enable()

path = os.environ.get('PATH_INFO', '')
method = os.environ.get('REQUEST_METHOD', '')

def main():
    pathSplit = path.strip('/').split('/')

    if not pathSplit or pathSplit[0] == '':
        homePageRoute()
        return

    if(pathSplit[0] == "students"): # a request regarding students

        if method == "DELETE" and len(pathSplit) == 2: # delete a student ROUTE
            try:
                student_id = int(pathSplit[1])
            except ValueError:
                badRequest("Invalid Student ID")
                return

            try:
                conn = connectToDB()
                cursor = conn.cursor()

                # see if student exists
                cursor.execute("SELECT id FROM students WHERE id = ?", (student_id,))
                if not cursor.fetchone():
                    conn.close()
                    notFound(path)
                    return
                
                # delete student from registration
                cursor.execute("DELETE FROM registrations WHERE student_id = ?", (student_id,))

                # and delete the actual student
                cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))

                conn.commit()
                conn.close()
                print("Status: 303 See Other")
                print("Location: /students")
                print("Content-Type: text/plain\n")
                return
            except Exception as e:
                badRequest("Internal Server Error (Manual)")
                return


        if method == "PUT" and len(pathSplit) == 2:
            try:
                student_id = int(pathSplit[1])
            except ValueError:
                badRequest("Invalid student ID given")
                return

            length = int(os.environ.get('CONTENT_LENGTH', 0))
            body = sys.stdin.read(length)

            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                badRequest("Invalid JSON input")
                return

            new_name = data.get("name")
            if not new_name.strip():
                badRequest("Bad input for new name")
                return

            # connect to database
            conn = connectToDB()
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM students WHERE id = ?", (student_id,))
            if not cursor.fetchone():
                conn.close()
                badRequest("student not found")
                return

            #otherwise we found the name
            cursor.execute("UPDATE students SET name = ? WHERE id = ?", (new_name, student_id))
            conn.commit()
            conn.close()
            # Redirect to updated student
            print("Status: 303 See Other")
            print(f"Location: /students/{student_id}")
            print("Content-Type: text/plain\n")
            return


        if(method == "GET" and len(pathSplit) < 2): # [ROUTE 1] get ALL students
            try:
                conn = connectToDB()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM students")
                rows = cursor.fetchall()

                students = []
                for row in rows:
                    student_id = int(row[0])

                    # find each class the student is enrolled in
                    cursor.execute(
                    """
                        SELECT c.id
                        FROM registrations r
                        JOIN courses c ON r.course_id = c.id
                        WHERE r.student_id = ?
                    """, (student_id,))

                    class_rows = cursor.fetchall()

                    classes = [class_row[0] for class_row in class_rows]

                    students.append({
                        "id": row[0],
                        "name": row[1],
                        "link": f"{Server_Info["url"]}/students/{row[0]}",
                        "courses": classes
                    })

                conn.close()

                # CGI headers
                print("Status: 200 OK")
                print("Content-Type: application/json\n")
                print(json.dumps(students, indent=4))

            except Exception as e:
                print("Status: 500 Internal Server Error")
                print("Content-Type: text/plain\n")
                print(f"Database error: {e}")


        elif method == "GET" and len(pathSplit) > 1: # [ROUTE 2] get a Specific student
            try:
                student_id = int(pathSplit[1])
            except ValueError:
                invalidRequest()
                return
            try:
                conn = connectToDB()
                cursor = conn.cursor()
                cursor.execute("SELECT id, name FROM students WHERE id = ?", (student_id,))
                row = cursor.fetchone()
                conn.close()

                if row:
                    result = {
                            "id": row[0],
                            "name": row[1],
                            }

                    print("Status: 200 OK")
                    print("Content-Type: application/json\n")
                    print(json.dumps(result, indent=4))
                    return
                else:
                    notFound(path)
                    return
            except Exception as e:
                print("Status: 500 Internal Server Error")
                print("Content-Type: text/plain\n")
                print(f"Database error: {e}")
                return

        elif method == "POST" and len(pathSplit) == 3 and pathSplit[2] == "courses":
            try:
                student_id = int(pathSplit[1])
            except ValueError:
                invalidRequest()
                return

            length = int(os.environ.get('CONTENT_LENGTH', 0))
            body = sys.stdin.read(length)

            try:
                course_id = json.loads(body)
            except json.JSONDecodeError:
                invalidRequest("Invalid JSON")
                return

            if not isinstance(course_id, str):
                invalidRequest("Course ID must be a string")
                return

            try:
                conn = connectToDB()
                cursor = conn.cursor()

                # Register student in course
                cursor.execute("INSERT INTO registrations (student_id, course_id) VALUES (?, ?)", (student_id, course_id))
                conn.commit()
                conn.close()

                # Return redirect
                print("Status: 303 See Other")
                print(f"Location: /students/{student_id}")
                print("Content-Type: text/plain\n")

            except Exception as e:
                print("Status: 500 Internal Server Error")
                print("Content-Type: application/json\n")
                print(json.dumps({"error": str(e)}))

        elif method == "POST" and len(pathSplit) == 1: # [ROUTE 3] post students 
            length = int(os.environ.get('CONTENT_LENGTH', 0))
            body = sys.stdin.read(length)

            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                print("Status: 400 Bad Request")
                print("Content-Type: application/json\n")
                print(json.dumps({"error": "Invalid JSON"}))
                return

            student_id = data.get('id')
            name = data.get('name')

            if not isinstance(student_id, int) or not isinstance(name, str) or not name.strip():
                print("Status: 400 Bad Request")
                print("Content-Type: application/json\n")
                print(json.dumps({"error": "Invalid input data"}))
                return

            try:
                conn = connectToDB()
                cursor = conn.cursor()

                # Check for existing student
                cursor.execute("SELECT id FROM students WHERE id = ?", (student_id,))
                if cursor.fetchone():
                    print("Status: 409 Conflict")
                    print("Content-Type: application/json\n")
                    print(json.dumps({"error": "Student ID already exists"}))
                    return

                # Insert student
                cursor.execute("INSERT INTO students (id, name) VALUES (?, ?)", (student_id, name))
                conn.commit()
                conn.close()

                # Redirect
                print("Status: 303 See Other")
                print(f"Location: /students/{student_id}")
                print("Content-Type: text/plain\n")

            except Exception as e:
                print("Status: 500 Internal Server Error")
                print("Content-Type: application/json\n")
                print(json.dumps({"error": f"Database error: {str(e)}"}))


        else:
            invalidRequest()
            
    elif pathSplit[0] == "courses": # a request regarding courses

        if method == "DELETE" and len(pathSplit) == 2:
            course_id = pathSplit[1]

            if not course_id.strip():
                badRequest("Invalid course ID")
                return

            try:
                conn = connectToDB()
                cursor = conn.cursor()

                # check if course exists
                cursor.execute("SELECT id FROM courses WHERE id = ?", (course_id,))
                if not cursor.fetchone():
                    conn.close()
                    notFound(path)
                    return

                # check if any students are registered for this course
                # if so we cant delete it
                cursor.execute("SELECT * FROM registrations WHERE course_id = ?", (course_id,))
                if cursor.fetchone():
                   conn.close()
                   badRequest("cannot delete  a course that students are registered for")
                   return
                
                # if no students take this course we can delete it.
                cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))

                conn.commit()
                conn.close()
                print("Status: 303 See Other")
                print("Location: /courses")
                print("Content-Type: text/plain\n")
                return
                   
            except Exception as e:
                badRequest("Manual Internal Server Error")
        
        if(method == "GET" and len(pathSplit) < 2): # [ROUTE ] get ALL courses
            try:
                conn = connectToDB()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM courses")
                rows = cursor.fetchall()
                conn.close()

                courses = []
                for row in rows:
                    courses.append({
                        "id": row[0],
                        "link": f"{Server_Info["url"]}/courses/{row[0]}"
                    })

                # CGI headers
                print("Status: 200 OK")
                print("Content-Type: application/json\n")
                print(json.dumps(courses, indent=4))

            except Exception as e:
                print("Status: 500 Internal Server Error")
                print("Content-Type: text/plain\n")
                print(f"Database error: {e}")

        elif method == "GET" and len(pathSplit) > 1: # [ROUTE 2] get a Specific course
            try:
                course_id = pathSplit[1].strip()
            except ValueError:
                invalidRequest()
                return
            try:
                conn = connectToDB()
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM courses WHERE id = ?", (course_id,))
                row = cursor.fetchone()
                conn.close()

                if row:
                    result = {
                            "id": row[0],
                            "link": f"{Server_Info["url"]}/courses/{course_id}",
                            }

                    print("Status: 200 OK")
                    print("Content-Type: application/json\n")
                    print(json.dumps(result, indent=4))
                    return
                else:
                    notFound(path)
                    return
            except Exception as e:
                print("Status: 500 Internal Server Error")
                print("Content-Type: text/plain\n")
                print(f"Database error: {e}")
                return

        elif method == "POST" and len(pathSplit) == 1: # [ROUTE 3] post a course
            length = int(os.environ.get('CONTENT_LENGTH', 0))
            body = sys.stdin.read(length)

            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                print("Status: 400 Bad Request")
                print("Content-Type: application/json\n")
                print(json.dumps({"error": "Invalid JSON"}))
                return

            course_id = data.get('id')

            if not isinstance(course_id,str) or not course_id.strip(): 
                print("Status: 400 Bad Request")
                print("Content-Type: application/json\n")
                print(json.dumps({"error": "Invalid input data"}))
                return

            try:
                conn = connectToDB()
                cursor = conn.cursor()

                # Check for existing course
                cursor.execute("SELECT id FROM courses WHERE id = ?", (course_id ))
                if cursor.fetchone():
                    print("Status: 409 Conflict")
                    print("Content-Type: application/json\n")
                    print(json.dumps({"error": "Course ID already exists"}))
                    return

                # Insert student
                cursor.execute("INSERT INTO courses (id) VALUES (?)", (course_id))
                conn.commit()
                conn.close()

                # Redirect
                print("Status: 303 See Other")
                print(f"Location: /students/{student_id}")
                print("Content-Type: text/plain\n")

            except Exception as e:
                print("Status: 500 Internal Server Error")
                print("Content-Type: application/json\n")
                print(json.dumps({"error": f"Database error: {str(e)}"}))

        else:
            invalidRequest()



        

    else:
        invalidRequest();

def notFound(path_input):
    print("Status: 404 Not Found")
    print("Content-Type: text/html\n")
    print(f'<html><body> <p><font size=+3><b>404 Not Found</b></font> <p>PATH_INFO: {path_input} </body></html>')
    return

def badRequest(error):
    print("Status: 400 Bad Request")
    print("Content-Type: application/json\n")
    print(json.dumps({"error": error}))
    return

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
