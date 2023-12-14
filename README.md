Models:
- Users
  - uuid
  - email
  - display name
  - password
- Databases
  - uuid
  - path
  - name
  - description
  - user_uuid => user.uuid
- Applications
  - uuid
  - name
  - description
  - base url
  - data policy url
  - user_uuid => user.uuid
- Tokens
  - uuid
  - database_uuid => database.uuid
  - token
  - expiration
  - refresh_token
Column Name	Data Type	Description
token_id	String/UUID	Unique identifier for the token.
user_id	String/UUID	Identifier linking the token to a specific user.
access_token	String	The actual access token.
refresh_token	String	The refresh token.
access_expires	Timestamp	Expiration time of the access token.
refresh_expires	Timestamp	Expiration time of the refresh token.
scope	String	The scope of access granted by the token.
client_id	String	Identifier for the client application. (user or application UUID)

https://sagarag.medium.com/how-do-you-discover-the-oauth2-server-configuration-d42d30ad5b9d
https://stackoverflow.com/questions/10205744/opening-sqlite3-database-from-python-in-read-only-mode
https://developer.okta.com/docs/reference/api/oidc/#response-properties-10
con = sqlite3.connect("file:tutorial.db?mode=ro", uri=True)
https://quart.palletsprojects.com/en/latest/tutorials/api_tutorial.html
