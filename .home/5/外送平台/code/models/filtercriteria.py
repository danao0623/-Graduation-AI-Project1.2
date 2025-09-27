```python
class FilterCriteria:
    def __init__(self, minRating=None, maxPrice=None, cuisineType=None):
        self.minRating = minRating
        self.maxPrice = maxPrice
        self.cuisineType = cuisineType