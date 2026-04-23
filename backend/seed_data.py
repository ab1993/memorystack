from app.database import SessionLocal
from app.models import AtomicNote
import json

def seed():
    db = SessionLocal()

    # Check if we already have data
    if db.query(AtomicNote).first():
        print("Data already exists. Skipping seed.")
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
    print("Seeded 3 core topics into MemoryStack!")

if __name__ == "__main__":
    seed()