```python
class AuthenticationController:
    def __init__(self):
        self.currentUser = None

    def checkUserPermission(self):
        if self.currentUser is None:
            return False
        # Add permission check logic here based on currentUser attributes
        return True