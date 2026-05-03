#
# Copyright (c) 2026 Abhishek Sharma. All rights reserved.
# This code is part of the MemoryStack project.
# Unauthorized copying or distribution of this file via any medium is strictly prohibited.
# Proprietary and confidential.
#

# seeddata.py
from app.database import SessionLocal
from app.models import AtomicNote, User

def seed():
    db = SessionLocal()

    # 1. SEED THE USER FIRST
    test_user = db.query(User).filter(User.id == 1).first()
    if not test_user:
        print("Creating User #1...")
        # Note: Depending on your Postgres setup, you might not need to manually set id=1
        # if it's auto-incrementing, but we will force it for our beta test.
        new_user = User(id=1, email="beta@memorystack.com")
        db.add(new_user)
        db.commit()

    # 2. SEED THE NOTES
    if db.query(AtomicNote).first():
        print("Notes already exist. Skipping note seed.")
        return

    notes = [
        AtomicNote(
            topic="Sliding Window",
            category="Data Structures",
            layer_1_gist="A technique for tracking a subset of data (a 'window') in a linear structure like an array or string to reduce time complexity from O(N²) to O(N).",
            layer_2_pattern="Use when you need to find a sub-array or sub-string that satisfies a certain condition (e.g., longest, shortest, target sum). Look for keywords like 'contiguous' or 'k-length'.",
            layer_3_questions=["Longest Substring Without Repeating Characters", "Minimum Size Subarray Sum", "Permutation in String"]
        ),
        AtomicNote(
            topic="Two Pointers",
            category="Data Structures",
            layer_1_gist="Using two indices (typically 'left' and 'right') to traverse a data structure simultaneously to find pairs or process elements efficiently.",
            layer_2_pattern="Commonly used on sorted arrays. One pointer starts at the beginning and one at the end (for sums) or both start at the beginning but move at different speeds (Fast & Slow).",
            layer_3_questions=["Two Sum II", "3Sum", "Container With Most Water", "Remove Duplicates from Sorted Array"]
        ),
        AtomicNote(
            topic="Load Balancer",
            category="System Design",
            layer_1_gist="A component that sits between clients and servers to distribute incoming network traffic across multiple servers to ensure high availability and reliability.",
            layer_2_pattern="Essential for horizontal scaling. Common algorithms include Round Robin, Least Connections, and IP Hash. Can be hardware-based or software-based (like Nginx/HAProxy).",
            layer_3_questions=["How does a Load Balancer handle session persistence?", "What is the difference between Layer 4 and Layer 7 Load Balancing?"]
        )
    ]

    db.add_all(notes)
    db.commit()
    print("✅ Seeded User #1 and 3 core topics into Postgres!")

if __name__ == "__main__":
    seed()