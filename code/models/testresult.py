```python
import datetime

class TestResult:
    def __init__(self, testResultId, testCaseId, result, timestamp):
        self.testResultId = testResultId
        self.testCaseId = testCaseId
        self.result = result
        self.timestamp = timestamp

    def __eq__(self, other):
        return (self.testResultId, self.testCaseId, self.result, self.timestamp) == (other.testResultId, other.testCaseId, other.result, other.timestamp)

    def __hash__(self):
        return hash((self.testResultId, self.testCaseId, self.result, self.timestamp))


# Example usage (replace with your actual data and logic)
test_result_1 = TestResult(1, 101, "Pass", datetime.datetime.now())
test_result_2 = TestResult(2, 102, "Fail", datetime.datetime.now())
test_result_3 = TestResult(1, 101, "Pass", datetime.datetime.now())


test_results = [test_result_1, test_result_2, test_result_3]

#Demonstrates handling duplicate objects.  Note that this depends on the __eq__ and __hash__ methods being correctly implemented.
unique_test_results = list(set(test_results))

print(len(test_results)) # Output: 3
print(len(unique_test_results)) # Output: 2

for result in unique_test_results:
    print(result.testResultId, result.testCaseId, result.result, result.timestamp)