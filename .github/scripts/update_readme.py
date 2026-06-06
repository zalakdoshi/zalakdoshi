import os
import re
import requests
from datetime import datetime, date, timedelta

def get_stats():
    url = "https://github-contributions-api.deno.dev/zalakdoshi.json"
    response = requests.get(url)
    data = response.json()

    contributions_list = []
    for week in data.get("contributions", []):
        for day in week:
            contributions_list.append(day)

    # Filter out days with contributions > 0
    active_days = [day for day in contributions_list if day["contributionCount"] > 0]
    active_days.sort(key=lambda x: x["date"])

    # 1. Total Contributions
    total_contributions = sum(day["contributionCount"] for day in contributions_list)

    # 2. Longest Streak
    longest_streak = 0
    temp_streak = 0
    prev_date = None

    for day in active_days:
        current_date = datetime.strptime(day["date"], "%Y-%m-%d").date()
        if prev_date is None:
            temp_streak = 1
        elif current_date - prev_date == timedelta(days=1):
            temp_streak += 1
        else:
            if temp_streak > longest_streak:
                longest_streak = temp_streak
            temp_streak = 1
        prev_date = current_date

    if temp_streak > longest_streak:
        longest_streak = temp_streak

    # 3. Current Streak
    current_streak = 0
    streak_start = None
    streak_end = None
    if active_days:
        last_active_date = datetime.strptime(active_days[-1]["date"], "%Y-%m-%d").date()
        today = date.today()
        
        # If the user has contributed today or yesterday, the streak is alive
        if last_active_date >= today - timedelta(days=1):
            current_streak = 1
            streak_end = last_active_date
            streak_start = last_active_date
            prev_date = last_active_date
            for day in reversed(active_days[:-1]):
                curr_date = datetime.strptime(day["date"], "%Y-%m-%d").date()
                if prev_date - curr_date == timedelta(days=1):
                    current_streak += 1
                    streak_start = curr_date
                    prev_date = curr_date
                elif prev_date - curr_date == timedelta(days=0):
                    continue
                else:
                    break

    # Format streak dates if they exist
    if streak_start and streak_end:
        start_fmt = streak_start.strftime("%b %d")
        end_fmt = streak_end.strftime("%b %d")
        streak_date_range = f" ({start_fmt} – {end_fmt})"
    else:
        streak_date_range = ""

    # Longest streak range calculation
    longest_streak_start = None
    longest_streak_end = None
    temp_streak = 0
    temp_start = None
    prev_date = None
    
    for day in active_days:
        current_date = datetime.strptime(day["date"], "%Y-%m-%d").date()
        if prev_date is None:
            temp_streak = 1
            temp_start = current_date
        elif current_date - prev_date == timedelta(days=1):
            temp_streak += 1
        else:
            if temp_streak >= longest_streak:
                longest_streak = temp_streak
                longest_streak_start = temp_start
                longest_streak_end = prev_date
            temp_streak = 1
            temp_start = current_date
        prev_date = current_date

    if temp_streak >= longest_streak:
        longest_streak = temp_streak
        longest_streak_start = temp_start
        longest_streak_end = prev_date

    if longest_streak_start and longest_streak_end:
        long_start_fmt = longest_streak_start.strftime("%b %d")
        long_end_fmt = longest_streak_end.strftime("%b %d")
        longest_streak_date_range = f" ({long_start_fmt} – {long_end_fmt})"
    else:
        longest_streak_date_range = ""

    start_year_fmt = "Aug 29, 2023"

    stats_text = (
        f"**Total Contributions:** {total_contributions} ({start_year_fmt} – Present)\n\n"
        f"**Current Streak:** {current_streak} {'days' if current_streak != 1 else 'day'}{streak_date_range}\n\n"
        f"**Longest Streak:** {longest_streak} {'days' if longest_streak != 1 else 'day'}{longest_streak_date_range}"
    )
    return stats_text

def update_readme():
    stats_text = get_stats()
    
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        # Look one level up if run from script folder
        readme_path = "../../README.md"
        if not os.path.exists(readme_path):
            readme_path = "d:/Placement/README.md"
            
    with open(readme_path, "r", encoding="utf-8") as file:
        content = file.read()

    pattern = r"(<!-- STATS_START -->\n)(.*?)(\n<!-- STATS_END -->)"
    new_content = re.sub(pattern, rf"\1{stats_text}\3", content, flags=re.DOTALL)

    with open(readme_path, "w", encoding="utf-8") as file:
        file.write(new_content)
    print("README stats updated successfully!")

if __name__ == "__main__":
    update_readme()
