import os
import secrets

# Generate a random secret key
secret_key = secrets.token_hex(16)

# Set the secret key as an environment variable
os.environ['FLASK_SECRET_KEY'] = secret_key