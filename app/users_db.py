from passlib.context import CryptContext
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
import os
from app.config import MONGODB_URI
import certifi

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# MongoDB connection setup
def connect_to_mongodb():
    try:
        # Use environment variable for MongoDB URI
        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            tls=True,
            tlsCAFile=certifi.where()
        )
        
        # Test the connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        
        # Select the database
        db = client['mydatabase']
        
        # Create a unique index on username to prevent duplicates
        db['users'].create_index("username", unique=True)
        return db
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Create admin user
def create_admin_user(db):
    try:
        users_collection = db['users']
        admin = {
            "username": "admin",
            "hashed_password": "adminpass",  # Hash the password
            "role": "admin",
            "access": []
        }
        result = users_collection.insert_one(admin)
        print(f"Admin user created with ID: {result.inserted_id}")
        return result.inserted_id
    except DuplicateKeyError:
        print("Error: Username 'admin' already exists in the database.")
        return None
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return None

# Verify admin user
def verify_admin_user(db, username: str, password: str) -> bool:
    try:
        users_collection = db['users']
        user = users_collection.find_one({"username": username})
        if user and verify_password(password, user['hashed_password']):
            print(f"User {username} authenticated successfully!")
            return True
        else:
            print(f"Authentication failed for user {username}.")
            return False
    except Exception as e:
        print(f"Error verifying user: {e}")
        return False

# Main execution
if __name__ == "__main__":
    # Connect to MongoDB
    db = connect_to_mongodb()
    if db is None:
        print("Exiting due to MongoDB connection failure.")
        exit(1)

    # Create admin user
    create_admin_user(db)

    # Verify the admin user
    verify_admin_user(db, "admin", "adminpass")

    # Close the MongoDB connection (optional)
    client = db.client
    client.close()
