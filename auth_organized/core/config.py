# Central place for auth-related settings.
# In a real project these should be read from environment variables (.env),
# not hardcoded here — but this is a straight move of what was already in
# auth/main.py, so behavior is unchanged for now.

SECRET_KEY = "yEUgLlGDn4jan9ClqaxjfNNgozbppER3xTVgYW16jbQ"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Identifies which client application is allowed to log in.
VALID_CLIENT_ID = "my-app-client"
VALID_CLIENT_SECRET = "super-secret-value"
