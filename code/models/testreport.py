```python
class TestReport:
    def __init__(self, reportId, timestamp, reportContent):
        self.reportId = reportId
        self.timestamp = timestamp
        self.reportContent = reportContent

```python
class TestReport:
    def __init__(self, reportId, submitterId, submissionTime, reportContent, testItems):
        self.reportId = reportId
        self.submitterId = submitterId
        self.submissionTime = submissionTime
        self.reportContent = reportContent
        self.testItems = testItems

class TestItem:
    def __init__(self, itemId, itemName, itemResult):
        self.itemId = itemId
        self.itemName = itemName
        self.itemResult = itemResult