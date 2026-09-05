"""
Pure-Python intelligence engine.

Hard rule: nothing in this package makes a network call or imports anything
from `app.providers`. Every function here takes plain numbers/series in and
returns plain, explainable numbers out, so it is testable without any external
API and without a database. This is what backend/tests/ exercises directly.
"""
