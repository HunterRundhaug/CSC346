#!/venv/bin/python

import pyodbc

try:
    conn = pyodbc.connect(
    'DRIVER={ODBC Driver 18 for SQL Server};'
    'SERVER=school-sql-server.database.windows.net,1433;'
    'DATABASE=school_sqlDB;'
    'UID=hunter@school-sql-server;'
    'PWD=Williewoo1;'
    'Encrypt=yes;'
    'TrustServerCertificate=no;'
    'Connection Timeout=30;'
    )
    print("Connection successful!")

    # Create a cursor
    cursor = conn.cursor()

    # Run a simple SELECT query
    cursor.execute("SELECT * FROM students")

    # Fetch all results
    rows = cursor.fetchall()

    # Print out each row
    for row in rows:
        print(row)

    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
