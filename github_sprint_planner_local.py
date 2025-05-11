#!/usr/bin/env python3
import json
import datetime
from datetime import timedelta
import sys
import os
from tabulate import tabulate

# Local storage directories
OUTPUT_DIR = "local_github_simulation"
MILESTONES_DIR = os.path.join(OUTPUT_DIR, "milestones")
ISSUES_DIR = os.path.join(OUTPUT_DIR, "issues")


def setup_local_storage():
    """Set up local storage directories."""
    for directory in [OUTPUT_DIR, MILESTONES_DIR, ISSUES_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")


def create_milestones(repo_owner, repo_name, sprint_names, start_date=None):
    """Create sprint milestones with appropriate due dates locally."""
    if start_date is None:
        start_date = datetime.datetime.now()
    
    milestones = {}
    
    for i, sprint_name in enumerate(sprint_names):
        # Calculate due date (one week per sprint from start date)
        due_date = start_date + timedelta(days=7 * (i + 1))
        
        # Milestone details
        milestone = {
            "number": i + 1,
            "title": sprint_name,
            "description": f"Sprint {i+1} tasks",
            "due_on": due_date.strftime("%Y-%m-%d"),
            "repository": f"{repo_owner}/{repo_name}"
        }
        
        # Save milestone to file
        milestone_file = os.path.join(MILESTONES_DIR, f"{sprint_name.replace(' ', '_')}.json")
        with open(milestone_file, 'w') as f:
            json.dump(milestone, f, indent=2)
        
        print(f"Created milestone: {sprint_name} (due: {due_date.strftime('%Y-%m-%d')})")
        
        milestones[i+1] = milestone
    
    return milestones


def create_issue(repo_owner, repo_name, title, description, milestone, assignee=None, labels=None):
    """Create a simulated GitHub issue locally."""
    # Generate a unique issue number (timestamp-based)
    issue_number = int(datetime.datetime.now().timestamp() % 100000)
    
    # Issue details
    issue = {
        "number": issue_number,
        "title": title,
        "body": description,
        "milestone": milestone,
        "assignee": assignee,
        "labels": labels or [],
        "repository": f"{repo_owner}/{repo_name}",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save issue to file
    issue_file = os.path.join(ISSUES_DIR, f"issue_{issue_number}.json")
    with open(issue_file, 'w') as f:
        json.dump(issue, f, indent=2)
    
    return issue


def load_user_stories(json_file):
    """Load user stories from a JSON file."""
    try:
        with open(json_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        raise ValueError(f"Error loading JSON file {json_file}: {e}")


def main():
    """Main function to simulate GitHub sprint planning locally."""
    # Check command line arguments
    if len(sys.argv) != 4:
        print("Usage: python github_sprint_planner_local.py <owner> <repo_name> <stories_json_file>")
        sys.exit(1)
    
    owner = sys.argv[1]
    repo_name = sys.argv[2]
    stories_file = sys.argv[3]
    
    try:
        # Setup local storage directories
        setup_local_storage()
        
        print(f"Running local simulation for repository: {owner}/{repo_name}")
        
        # Create sprint milestones
        sprint_names = ["Sprint 1", "Sprint 2"]
        milestones = create_milestones(owner, repo_name, sprint_names)
        
        # Save milestone index
        milestone_index = {
            "repository": f"{owner}/{repo_name}",
            "milestones": milestones
        }
        with open(os.path.join(OUTPUT_DIR, "milestone_index.json"), 'w') as f:
            json.dump(milestone_index, f, indent=2)
        
        # Load user stories
        stories = load_user_stories(stories_file)
        
        # Create issues for each story
        issue_data = []
        for story in stories:
            title = story.get('title')
            description = story.get('description', '')
            assignee = story.get('assignee')
            labels = story.get('labels', [])
            sprint_number = story.get('sprint')
            
            if not title or not sprint_number:
                print(f"Skipping invalid story (missing title or sprint number): {story}")
                continue
            
            if sprint_number not in milestones:
                print(f"Invalid sprint number: {sprint_number}. Skipping story: {title}")
                continue
            
            # Create the issue
            issue = create_issue(
                repo_owner=owner,
                repo_name=repo_name,
                title=title,
                description=description,
                milestone=milestones[sprint_number],
                assignee=assignee,
                labels=labels
            )
            
            print(f"Created issue #{issue['number']}: {title}")
            issue_data.append([
                issue['number'],
                title,
                assignee or "Unassigned",
                f"Sprint {sprint_number}"
            ])
        
        # Save all issues index
        issue_index = {
            "repository": f"{owner}/{repo_name}",
            "issues": issue_data
        }
        with open(os.path.join(OUTPUT_DIR, "issue_index.json"), 'w') as f:
            json.dump(issue_index, f, indent=2)
        
        # Print summary table
        print("\nSprint Planning Summary:")
        headers = ["Issue #", "Title", "Assignee", "Sprint"]
        print(tabulate(issue_data, headers=headers, tablefmt="grid"))
        
        # Print instructions for viewing the results
        print("\nLocal GitHub simulation complete!")
        print(f"All data has been saved to the '{OUTPUT_DIR}' directory.")
        print(f"- Milestones are in: {MILESTONES_DIR}")
        print(f"- Issues are in: {ISSUES_DIR}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 