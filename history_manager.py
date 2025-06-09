import csv
import os
from typing import List, Tuple


class HistoryManager:
    def __init__(self, filename="solved_history.csv"):
        self.filename = filename

    def save_history(self, problem: str, result) -> bool:
        """Save a solved problem to history file"""
        try:
            file_exists = os.path.isfile(self.filename)
            with open(self.filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['Problem', 'Result'])
                writer.writerow([problem, result])
            return True
        except Exception as e:
            print(f"Failed to save history: {e}")
            return False

    def load_history(self) -> List[Tuple[str, str]]:
        """Load history from file"""
        history_entries = []
        
        if not os.path.isfile(self.filename):
            return history_entries
            
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)  # Skip header
                
                for row in reader:
                    if len(row) >= 2:
                        problem, result = row[0], row[1]
                        history_entries.append((problem, result))
                        
        except Exception as e:
            print(f"Failed to load history: {e}")
            
        return history_entries

    def clear_history(self) -> bool:
        """Clear all history"""
        try:
            if os.path.isfile(self.filename):
                os.remove(self.filename)
            return True
        except Exception as e:
            print(f"Failed to clear history: {e}")
            return False

    def get_stats(self) -> dict:
        """Get statistics about solving history"""
        history = self.load_history()
        
        if not history:
            return {
                'total_problems': 0,
                'unique_problems': 0,
                'most_common': None
            }
        
        # Count unique problems
        problem_counts = {}
        for problem, _ in history:
            problem_counts[problem] = problem_counts.get(problem, 0) + 1
        
        # Find most common problem
        most_common = max(problem_counts.items(), key=lambda x: x[1]) if problem_counts else None
        
        return {
            'total_problems': len(history),
            'unique_problems': len(problem_counts),
            'most_common': most_common
        }
