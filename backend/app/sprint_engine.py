#
# Copyright (c) 2026 Abhishek Sharma. All rights reserved.
# This code is part of the MemoryStack project.
# Unauthorized copying or distribution of this file via any medium is strictly prohibited.
# Proprietary and confidential.
#

from datetime import datetime, date
import math

class SprintEngine:
    @staticmethod
    def generate_plan(interview_date_str: str, topics: list):
        """
        Calculates a dynamic revision schedule.
        interview_date_str: 'YYYY-MM-DD'
        topics: List of topic names from our DB
        """
        if not topics:
            return {"error": "No topics selected. Please select at least one topic."}

        try:
            # Try YYYY-MM-DD first (Standard API format)
            target_date = datetime.strptime(interview_date_str, "%Y-%m-%d").date()
        except ValueError:
            try:
                # Fallback for DD/MM/YYYY (User friendly format)
                target_date = datetime.strptime(interview_date_str, "%d/%m/%Y").date()
            except ValueError:
                return {"error": "Invalid date format. Please use YYYY-MM-DD or DD/MM/YYYY"}

        today = date.today()
        days_available = (target_date - today).days

        if days_available <= 0:
            return {"error": "Interview is too soon! Date must be in the future."}

        sprint_plan = []

        # Scenario A: Emergency Sprint (1-2 days)
        if days_available <= 2:
            for t in topics:
                sprint_plan.append({"day": "Day 1", "topic": t, "focus": "Gist & Patterns (Layers 1 & 2)", "status": "pending"})
                sprint_plan.append({"day": "Day 2", "topic": t, "focus": "Top Questions (Layer 3)", "status": "pending"})

        # Scenario B: Short Sprint (3-5 days)
        elif days_available <= 5:
            for t in topics:
                sprint_plan.append({"day": "Day 1-2", "topic": t, "focus": "Foundation (Layers 1 & 2)", "status": "pending"})
                sprint_plan.append({"day": "Day 3-5", "topic": t, "focus": "Deep Practice (Layer 3)", "status": "pending"})

        # Scenario C: Relaxed Prep (6+ days)
        else:
            for i, topic in enumerate(topics):
                day_num = i + 1
                if day_num < days_available:
                    sprint_plan.append({"day": f"Day {day_num}", "topic": topic, "focus": "Full Mastery (Layers 1-3)", "status": "pending"})
                else:
                    # Catch-all for remaining topics on the last available days
                    sprint_plan.append({"day": "Final Review", "topic": topic, "focus": "Quick Polish (Layers 1 & 2)", "status": "pending"})

        return {
            "target_date": target_date.strftime("%Y-%m-%d"),
            "metadata": {
                "days_allocated": days_available,
                "total_topics": len(topics),
                "intensity": "High" if days_available < 3 else "Moderate"
            },
            "sprint_plan": sprint_plan # 👈 Now a flat list ready for the frontend!
        }