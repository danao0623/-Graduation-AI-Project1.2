```python
class TestCase:
    def __init__(self, testCaseId, description):
        self.testCaseId = testCaseId
        self.description = description

```python
class TestCase:
    def __init__(self, testCaseId, testCaseName, testResult):
        self.testCaseId = testCaseId
        self.testCaseName = testCaseName
        self.testResult = testResult