#!/usr/bin/env python3
import os
import json
import datetime
from datetime import timedelta
import sys
from tabulate import tabulate
from github import Github
from github.GithubException import GithubException


def authenticate_github():
    """Authenticate to GitHub using a personal access token from environment variable."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set. Please set it with your GitHub personal access token.")
    
    try:
        github = Github(token)
        # Test authentication by getting the authenticated user
        github.get_user().login
        return github
    except GithubException as e:
        raise ConnectionError(f"Failed to authenticate with GitHub: {e}")


def get_repository(github, owner, repo_name):
    """Get the GitHub repository object."""
    try:
        return github.get_repo(f"{owner}/{repo_name}")
    except GithubException as e:
        raise ValueError(f"Failed to access repository {owner}/{repo_name}: {e}")


def create_milestones(repo, sprint_names, start_date=None):
    """Create sprint milestones with appropriate due dates."""
    if start_date is None:
        start_date = datetime.datetime.now()
    
    milestones = {}
    
    for i, sprint_name in enumerate(sprint_names):
        # Calculate due date (one week per sprint from start date)
        due_date = start_date + timedelta(days=7 * (i + 1))
        
        # Check if milestone already exists
        existing_milestones = list(repo.get_milestones(state="open"))
        milestone_exists = any(m.title == sprint_name for m in existing_milestones)
        
        if milestone_exists:
            print(f"Milestone '{sprint_name}' already exists. Skipping creation.")
            milestone = next(m for m in existing_milestones if m.title == sprint_name)
        else:
            milestone = repo.create_milestone(
                title=sprint_name,
                state="open",
                description=f"Sprint {i+1} tasks",
                due_on=due_date
            )
            print(f"Created milestone: {sprint_name} (due: {due_date.strftime('%Y-%m-%d')})")
        
        milestones[i+1] = milestone
    
    return milestones


def create_issue(repo, title, description, milestone, assignee=None, labels=None):
    """Create a GitHub issue with the specified details."""
    try:
        issue = repo.create_issue(
            title=title,
            body=description,
            milestone=milestone,
            assignee=assignee,
            labels=labels
        )
        return issue
    except GithubException as e:
        print(f"Error creating issue '{title}': {e}")
        return None


def load_user_stories(json_file):
    """Load user stories from a JSON file."""
    try:
        with open(json_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        raise ValueError(f"Error loading JSON file {json_file}: {e}")


def main():
    """Main function to automate GitHub sprint planning."""
    # Check command line arguments
    if len(sys.argv) != 4:
        print("Usage: python github_sprint_planner.py <owner> <repo_name> <stories_json_file>")
        sys.exit(1)
    
    owner = sys.argv[1]
    repo_name = sys.argv[2]
    stories_file = sys.argv[3]
    
    try:
        # Authenticate to GitHub
        github = authenticate_github()
        
        # Get repository
        repo = get_repository(github, owner, repo_name)
        
        # Create sprint milestones
        sprint_names = ["Sprint 1", "Sprint 2"]
        milestones = create_milestones(repo, sprint_names)
        
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
                repo=repo,
                title=title,
                description=description,
                milestone=milestones[sprint_number],
                assignee=assignee,
                labels=labels
            )
            
            if issue:
                print(f"Created issue #{issue.number}: {title}")
                issue_data.append([
                    issue.number,
                    title,
                    assignee or "Unassigned",
                    f"Sprint {sprint_number}"
                ])
        
        # Print summary table
        print("\nSprint Planning Summary:")
        headers = ["Issue #", "Title", "Assignee", "Sprint"]
        print(tabulate(issue_data, headers=headers, tablefmt="grid"))
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 