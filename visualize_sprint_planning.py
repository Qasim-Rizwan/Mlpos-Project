#!/usr/bin/env python3
import os
import json
import sys
from tabulate import tabulate

# Local storage directories
OUTPUT_DIR = "local_github_simulation"
MILESTONES_DIR = os.path.join(OUTPUT_DIR, "milestones")
ISSUES_DIR = os.path.join(OUTPUT_DIR, "issues")


def load_json_file(file_path):
    """Load data from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return None


def get_all_issues():
    """Get all issues from the local storage."""
    issues = []
    for filename in os.listdir(ISSUES_DIR):
        if filename.endswith('.json'):
            issue_path = os.path.join(ISSUES_DIR, filename)
            issue = load_json_file(issue_path)
            if issue:
                issues.append(issue)
    return issues


def get_all_milestones():
    """Get all milestones from the local storage."""
    milestones = []
    for filename in os.listdir(MILESTONES_DIR):
        if filename.endswith('.json'):
            milestone_path = os.path.join(MILESTONES_DIR, filename)
            milestone = load_json_file(milestone_path)
            if milestone:
                milestones.append(milestone)
    return milestones


def show_milestones(milestones):
    """Display milestones in a tabulated format."""
    if not milestones:
        print("No milestones found.")
        return
    
    milestone_data = []
    for milestone in milestones:
        milestone_data.append([
            milestone.get("number"),
            milestone.get("title"),
            milestone.get("description"),
            milestone.get("due_on")
        ])
    
    headers = ["Number", "Title", "Description", "Due Date"]
    print("\n=== MILESTONES ===")
    print(tabulate(milestone_data, headers=headers, tablefmt="grid"))


def show_issues_by_milestone(issues, milestones):
    """Display issues grouped by milestone."""
    if not issues:
        print("No issues found.")
        return
    
    # Create a milestone lookup dict for faster access
    milestone_lookup = {m.get("number"): m for m in milestones}
    
    # Group issues by milestone
    issues_by_milestone = {}
    for issue in issues:
        milestone_num = issue.get("milestone", {}).get("number")
        if milestone_num not in issues_by_milestone:
            issues_by_milestone[milestone_num] = []
        issues_by_milestone[milestone_num].append(issue)
    
    # Display issues for each milestone
    for milestone_num, milestone_issues in issues_by_milestone.items():
        milestone = milestone_lookup.get(milestone_num, {"title": f"Milestone {milestone_num}"})
        print(f"\n=== {milestone.get('title')} ===")
        
        issue_data = []
        for issue in milestone_issues:
            label_str = ", ".join(issue.get("labels", []))
            issue_data.append([
                issue.get("number"),
                issue.get("title"),
                issue.get("assignee") or "Unassigned",
                label_str
            ])
        
        headers = ["Issue #", "Title", "Assignee", "Labels"]
        print(tabulate(issue_data, headers=headers, tablefmt="grid"))


def show_issues_by_assignee(issues):
    """Display issues grouped by assignee."""
    if not issues:
        print("No issues found.")
        return
    
    # Group issues by assignee
    issues_by_assignee = {}
    for issue in issues:
        assignee = issue.get("assignee") or "Unassigned"
        if assignee not in issues_by_assignee:
            issues_by_assignee[assignee] = []
        issues_by_assignee[assignee].append(issue)
    
    # Display issues for each assignee
    print("\n=== ISSUES BY ASSIGNEE ===")
    for assignee, assignee_issues in issues_by_assignee.items():
        print(f"\nAssignee: {assignee}")
        
        issue_data = []
        for issue in assignee_issues:
            milestone_title = issue.get("milestone", {}).get("title", "No Milestone")
            issue_data.append([
                issue.get("number"),
                issue.get("title"),
                milestone_title,
                ", ".join(issue.get("labels", []))
            ])
        
        headers = ["Issue #", "Title", "Sprint", "Labels"]
        print(tabulate(issue_data, headers=headers, tablefmt="simple"))


def main():
    """Main function to visualize sprint planning data."""
    # Check if the local storage exists
    if not os.path.exists(OUTPUT_DIR):
        print(f"Error: Local storage directory '{OUTPUT_DIR}' not found.")
        print("Run github_sprint_planner_local.py first to generate the data.")
        sys.exit(1)
    
    # Load all data
    issues = get_all_issues()
    milestones = get_all_milestones()
    
    # Show milestones
    show_milestones(milestones)
    
    # Show issues by milestone
    show_issues_by_milestone(issues, milestones)
    
    # Show issues by assignee
    show_issues_by_assignee(issues)


if __name__ == "__main__":
    main() 