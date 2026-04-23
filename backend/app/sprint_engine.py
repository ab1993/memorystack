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
            return {"error": "Interview is too soon! Focus on Layer 1 (Gists) only."}

        plan = {}

        # Scenario A: Emergency Sprint (1-2 days)
        if days_available <= 2:
            plan["Day 1"] = [{"topic": t, "focus": "Gist & Patterns", "layers": [1, 2]} for t in topics]
            plan["Day 2"] = [{"topic": t, "focus": "Top Questions", "layers": [3]} for t in topics]

        # Scenario B: Short Sprint (3-5 days)
        elif days_available <= 5:
            # Split topics into two halves
            mid = math.ceil(len(topics) / 2)
            plan["Day 1-2"] = [{"topic": t, "focus": "Foundation", "layers": [1, 2]} for t in topics]
            plan["Day 3-5"] = [{"topic": t, "focus": "Deep Practice", "layers": [3]} for t in topics]

        # Scenario C: Relaxed Prep (6+ days)
        else:
            # Spread topics out
            for i, topic in enumerate(topics):
                day_num = i + 1
                if day_num < days_available:
                    plan[f"Day {day_num}"] = [{"topic": topic, "focus": "Full Mastery", "layers": [1, 2, 3]}]
                else:
                    # Catch-all for remaining topics on the last available days
                    if "Final Review" not in plan: plan["Final Review"] = []
                    plan["Final Review"].append({"topic": topic, "focus": "Quick Polish", "layers": [1, 2]})

        return {
            "metadata": {
                "days_allocated": days_available,
                "total_topics": len(topics),
                "intensity": "High" if days_available < 3 else "Moderate"
            },
            "schedule": plan
        }