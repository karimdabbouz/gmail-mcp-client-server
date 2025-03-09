


## Important: Authenticating with Gmail

Manual OAuth authentication via the browser is required to work with Gmail. To do so, run server.py once as a standalone script with the credentials.json file next to the server.py script. It will then ask you to authenticate using your browser. After authenticating, the session is saved as token.pickle in the root of this project. You can then use this pickle file to start the client and server via the client.py file.

Information on authentication with Gmail and getting the credentials.json file: https://developers.google.com/gmail/api/quickstart/python