#!/home/ubuntu/oci-env/bin/python3

def dashboard_html(username):
	return (f"""
	    <html>
	    <head>
		<title>Cloud VM Dashboard</title>
	    </head>
	    <body>
		<h1>Welcome, {username}!</h1>

		<h2>Your Options:</h2>

		<!-- Create a new server -->
		<form method="post" action="/cgi-bin/CSC346/proj_7/create_server">
		    <label for="desc">Server Description:</label>
		    <input type="text" id="desc" name="description">
		    <input type="submit" value="Create New Server">
		</form>

		<br>

		<!-- View your existing servers -->
		<form method="get" action="/cgi-bin/CSC346/proj_7/api/servers/myservers">
		    <input type="submit" value="View My Servers">
		</form>

		<br>

		<!-- Terminate a server -->
		<form method="post" action="/cgi-bin/terminate_server.py">
		    <label for="server_id">Server ID to Terminate:</label>
		    <input type="text" id="server_id" name="server_id">
		    <input type="submit" value="Terminate Server">
		</form>

		<br>

		<!-- Logout -->
		<form method="get" action="/cgi-bin/CSC346/proj_7/api/login">
		    <input type="submit" value="Log Out">
		</form>

	    </body>
	    </html>
	    """)

def loginPage():
    return ("""
    <html>
    <head>
        <title>Login Required</title>
    </head>
    <body>
        <h2>You are not logged in</h2>
        <form method="post" action="/cgi-bin/CSC346/proj_7/api/login">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
            <input type="submit" value="Log In">
        </form>
    </body>
    </html>
    """)

