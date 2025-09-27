```python
from typing import Dict, Any

class User:
    def __init__(self, userId: int, username: str, password: str, role: str):
        self.userId = userId
        self.username = username
        self.password = password
        self.role = role

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.userId,
            "username": self.username,
            "password": self.password,
            "role": self.role
        }

#  This is a placeholder.  The actual implementation would require database interaction 
#  and potentially interaction with other microservices (e.g., using gRPC or Kafka).
#  The following functions are examples and would need to be adapted to your specific database and microservice architecture.

def create_user(user_data: Dict[str, Any]) -> User:
    #  In a real application, this would interact with a database (e.g., using SQLAlchemy or another ORM)
    #  to insert the user data.  Error handling and security measures (e.g., password hashing) are crucial.
    user = User(**user_data)
    # Simulate database insertion
    print(f"User created: {user.to_dict()}")
    return user

def get_user(user_id: int) -> User:
    #  In a real application, this would query the database to retrieve the user.
    #  Error handling (e.g., user not found) is important.
    # Simulate database retrieval
    dummy_user_data = {"userId": user_id, "username": "testuser", "password": "password", "role": "user"}
    user = User(**dummy_user_data)
    print(f"User retrieved: {user.to_dict()}")
    return user

def update_user(user_id: int, updates: Dict[str, Any]) -> User:
    # In a real application, this would update the user in the database.
    #  Error handling (e.g., user not found, invalid updates) is important.
    # Simulate database update
    print(f"User {user_id} updated with: {updates}")
    return get_user(user_id)

def delete_user(user_id: int) -> None:
    # In a real application, this would delete the user from the database.
    # Error handling (e.g., user not found) is important.
    # Simulate database deletion
    print(f"User {user_id} deleted.")