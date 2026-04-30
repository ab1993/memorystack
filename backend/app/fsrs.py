# backend/app/fsrs.py
from datetime import datetime, timedelta

def calculate_next_review(current_stability: float, difficulty: float, rating: int):
    """
    Simplified FSRS logic
    rating: 1 (Again), 2 (Hard), 3 (Good), 4 (Easy)
    stability: Days until the memory is 90% likely to be forgotten.
    """
    # multipliers for stability growth
    multipliers = {1: 0.1, 2: 1.2, 3: 2.5, 4: 4.0}

    # If topic is brand new (stability is 0 or None)
    if not current_stability or current_stability == 0:
        new_stability = 1.0 if rating > 1 else 0.1
    else:
        new_stability = current_stability * multipliers.get(rating, 1.0)

    # Calculate the timestamp for the next push
    next_date = datetime.utcnow() + timedelta(days=new_stability)

    return next_date, new_stability