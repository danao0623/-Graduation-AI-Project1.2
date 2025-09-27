```python
class User:
    def __init__(self, userId, username, password):
        self.userId = userId
        self.username = username
        self.password = password

```python
class User:
    def __init__(self, userId, username, password, role):
        self.userId = userId
        self.username = username
        self.password = password
        self.role = role

    def isValidPassword(self, password):
        return self.password == password