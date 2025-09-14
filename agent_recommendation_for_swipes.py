import json
import os
from datetime import datetime
from typing import Optional

from app_cool import ai_travel_agent_agno, ListOut
from preferences import user_preferences
from travel_info import travel_info


def run_and_save(output_path: Optional[str] = None) -> str:
    """
    Runs the recommendation agent and saves the returned ListOut to JSON.

    If output_path is not provided, writes to ./outputs/recommendations_YYYYmmdd_HHMMSS.json
    and returns the absolute path to the created file.
    """
    recs: ListOut = ai_travel_agent_agno(user_preferences, travel_info)
    data = recs.model_dump()

    if not output_path:
        base_dir = os.path.dirname(__file__)
        out_dir = os.path.join(base_dir, "outputs")
        os.makedirs(out_dir, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(out_dir, f"recommendations_{stamp}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved agent recommendations to: {output_path}")
    return output_path


if __name__ == "__main__":
    run_and_save()


