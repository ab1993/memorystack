#
# Copyright (c) 2026 Abhishek Sharma. All rights reserved.
# This code is part of the MemoryStack project.
# Unauthorized copying or distribution of this file via any medium is strictly prohibited.
# Proprietary and confidential.
#

from app.sprint_engine import SprintEngine
from datetime import date, timedelta
import json

def test_sprints():
    # Setup sample topics
    topics = ["Sliding Window", "Two Pointers", "Load Balancer", "Caching", "Sharding"]

    # 1. Test Case: Emergency Sprint (2 days away)
    print("\n--- TEST CASE 1: EMERGENCY (2 DAYS) ---")
    emergency_date = (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")
    plan_2d = SprintEngine.generate_plan(emergency_date, topics)
    print(json.dumps(plan_2d, indent=2))

    # 2. Test Case: Short Sprint (5 days away)
    print("\n--- TEST CASE 2: SHORT SPRINT (5 DAYS) ---")
    short_date = (date.today() + timedelta(days=5)).strftime("%Y-%m-%d")
    plan_5d = SprintEngine.generate_plan(short_date, topics)
    print(json.dumps(plan_5d, indent=2))

    # 3. Test Case: Standard Prep (10 days away)
    print("\n--- TEST CASE 3: STANDARD PREP (10 DAYS) ---")
    standard_date = (date.today() + timedelta(days=10)).strftime("%Y-%m-%d")
    plan_10d = SprintEngine.generate_plan(standard_date, topics)
    print(json.dumps(plan_10d, indent=2))

if __name__ == "__main__":
    test_sprints()