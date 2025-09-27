class TestItem:
    def __init__(self, testItemId, testItemName):
        self.testItemId = testItemId
        self.testItemName = testItemName
        self.completedTestCases = []

    def getCompletedTestCases(self):
        return self.completedTestCases

    def addTestCase(self, testCase):
        self.completedTestCases.append(testCase)


class TestCase:
    def __init__(self, testCaseId, testCaseName):
        self.testCaseId = testCaseId
        self.testCaseName = testCaseName

#Example Usage
testItem1 = TestItem(1, "Test Item 1")
testItem1.addTestCase(TestCase(101, "Test Case 101"))
testItem1.addTestCase(TestCase(102, "Test Case 102"))

completedTestCases = testItem1.getCompletedTestCases()
for testCase in completedTestCases:
    print(f"Test Case ID: {testCase.testCaseId}, Test Case Name: {testCase.testCaseName}")