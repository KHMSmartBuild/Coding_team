# Script: make_a_decision
# Requirements: Meeting notes, natural language processing libraries
# Purpose: Extract key decisions and action items from meeting notes to ensure follow-up and implementation.
# added functionalities to:
# -  load meeting notes, 
#  - extract key decisions and action items using natural language processing techniques, 
#   - generate a summary report. Here's an updated version of the script:

import re

class DecisionExtraction:
    def __init__(self, meeting_notes):
        self.meeting_notes = meeting_notes

    def load_meeting_notes(self, file_path):
        # Load meeting notes from a text file.
        with open(file_path, 'r') as file:
            self.meeting_notes = file.read()

    def extract_decisions_and_action_items(self):
        # Use regular expressions to identify decision and action item patterns in the meeting notes.
        decision_pattern = r'\b(decision|agreed|decided|resolved):\s*(.*)'
        action_item_pattern = r'\b(action item|next steps|to do|todo):\s*(.*)'

        decisions = re.findall(decision_pattern, self.meeting_notes, re.IGNORECASE)
        action_items = re.findall(action_item_pattern, self.meeting_notes, re.IGNORECASE)

        self.decisions = [d[1] for d in decisions]
        self.action_items = [a[1] for a in action_items]

    def generate_summary_report(self):
        # Generate a summary report containing extracted decisions and action items.
        summary_report = {
            'decisions': self.decisions,
            'action_items': self.action_items
        }

        self.summary_report = summary_report

# Usage example
decision_extraction = DecisionExtraction(None)
decision_extraction.load_meeting_notes('meeting_notes.txt')
decision_extraction.extract_decisions_and_action_items()
decision_extraction.generate_summary_report()
print(decision_extraction.summary_report)
