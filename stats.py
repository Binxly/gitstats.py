import calendar
import os
from datetime import datetime, timedelta
from scanner import GitRepositoryScanner
from typing import Dict, List

import git

# constants are used to create the graph and init the commits dir
# uses approximate values since close enough


class GitStats:
    DAYS_IN_LAST_6_MONTHS = 183
    WEEKS_IN_LAST_6_MONTHS = 26

    def __init__(self):
        self.dot_file = GitRepositoryScanner()._get_dot_file_path()

    def get_beginning_of_day(self, dt: datetime) -> datetime:
        return datetime(dt.year, dt.month, dt.day)

    def count_days_since_date(self, date: datetime) -> int:
        days = 0
        now = self.get_beginning_of_day(datetime.now())
        date = self.get_beginning_of_day(date)

        while date < now:
            date += timedelta(days=1)
            days += 1
            if days > self.DAYS_IN_LAST_6_MONTHS:
                return 99999
        return days

    def process_repositories(self, email: str) -> Dict[int, int]:
        with open(self.dot_file, "r") as f:
            repos = [line.strip() for line in f.readlines()]

        commits = {i: 0 for i in range(self.DAYS_IN_LAST_6_MONTHS + 1)}

        for repo_path in repos:
            try:
                repo = git.Repo(repo_path)
                try:
                    repo.head.reference
                    commits = self._fill_commits(repo, email, commits)
                except (ValueError, TypeError):
                    print(f"Warning: Repository at {repo_path} appears to be empty")
            except (git.InvalidGitRepositoryError, git.NoSuchPathError):
                print(f"Warning: {repo_path} is not a valid git repository")
                continue

        return commits

    def _fill_commits(
        self, repo: git.Repo, email: str, commits: Dict[int, int]
    ) -> Dict[int, int]:
        offset = self._calc_offset()

        for commit in repo.iter_commits():
            if commit.author.email != email:
                continue

            days_ago = self.count_days_since_date(commit.authored_datetime) + offset

            if days_ago != 99999:
                commits[days_ago] = commits.get(days_ago, 0) + 1

        return commits

    def _calc_offset(self) -> int:
        weekday = datetime.now().weekday()
        return 7 - weekday if weekday == 6 else 6 - weekday

    def print_stats(self, email: str) -> None:
        commits = self.process_repositories(email)
        self._print_commit_stats(commits)

    def _print_commit_stats(self, commits: Dict[int, int]) -> None:
        self._print_months()
        cols = self._build_columns(commits)
        self._print_cells(cols)

    def _build_columns(self, commits: Dict[int, int]) -> Dict[int, List[int]]:
        cols = {}
        for k in sorted(commits.keys()):
            week = k // 7
            day = k % 7

            if week not in cols:
                cols[week] = [0] * 7

            cols[week][day] = commits[k]

        return cols

    def _print_months(self) -> None:
        current = datetime.now()
        start_date = current - timedelta(days=self.DAYS_IN_LAST_6_MONTHS)

        print("         ", end="")
        current_month = start_date.month

        while start_date <= current:
            if start_date.month != current_month:
                print(f"{calendar.month_abbr[start_date.month]} ", end="")
                current_month = start_date.month
            else:
                print("    ", end="")
            start_date += timedelta(days=7)
        print()

    def _print_day_col(self, day: int) -> None:
        days = {1: " Mon ", 3: " Wed ", 5: " Fri "}
        print(days.get(day, "     "), end="")

    # colors
    def _print_cell(self, val: int, is_today: bool = False) -> None:
        if is_today:
            color = "\033[1;37;45m"  # magenta - current day
        elif val == 0:
            color = "\033[0;37;30m"  # dark gray - no commits
        elif val < 5:
            color = "\033[1;30;47m"  # light gray - < 5 commits
        elif val < 10:
            color = "\033[1;30;43m"  # yellow - < 10 commits
        else:
            color = "\033[1;30;42m"  # green

        reset = "\033[0m"

        if val == 0:
            print(f"{color}  - {reset}", end="")
        else:
            if val >= 100:
                print(f"{color}{val} {reset}", end="")
            elif val >= 10:
                print(f"{color} {val} {reset}", end="")
            else:
                print(f"{color}  {val} {reset}", end="")

    def _print_cells(self, cols: Dict[int, List[int]]) -> None:
        self._print_months()

        for day in range(6, -1, -1):  # Iterate days (Sun to Mon)
            for week in range(self.WEEKS_IN_LAST_6_MONTHS + 1, -1, -1):  # Iterate weeks (last 6 months to current)
                if week == self.WEEKS_IN_LAST_6_MONTHS + 1:
                    self._print_day_col(day)  # Print left day labels (Mon, Wed, Fri)

                # Check if week has data and day is within range
                if week in cols and len(cols[week]) > day:
                    is_today = week == 0 and day == self._calc_offset() - 1  # Check if today
                    self._print_cell(cols[week][day], is_today)  # Print commit count
                else:
                    self._print_cell(0, False)  # Print empty cell if no data
            print()  # Newline after each week
