#!/usr/bin/env python3
import os
import json
import datetime
from datetime import timedelta
import sys
import requests
from tabulate import tabulate


class GitHubAPI:
    """GitHub API client using direct REST API calls."""
    
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def _make_request(self, method, endpoint, data=None):
        """Make an HTTP request to the GitHub API."""
        url = f"{self.base_url}{endpoint}"
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            json=data
        )
        
        if response.status_code >= 400:
            raise Exception(f"API call failed: {response.status_code} - {response.text}")
        
        return response.json() if response.content else None
    
    def get_user(self):
        """Get the authenticated user."""
        return self._make_request("GET", "/user")
    
    def get_repository(self, owner, repo):
        """Get repository information."""
        return self._make_request("GET", f"/repos/{owner}/{repo}")
    
    def get_milestones(self, owner, repo, state="open"):
        """Get repository milestones."""
        return self._make_request("GET", f"/repos/{owner}/{repo}/milestones?state={state}")
    
    def create_milestone(self, owner, repo, title, description=None, due_on=None):
        """Create a repository milestone."""
        data = {
            "title": title,
            "state": "open",
            "description": description
        }
        
        if due_on:
            # Convert to ISO 8601 format
            data["due_on"] = due_on.isoformat()
        
        return self._make_request("POST", f"/repos/{owner}/{repo}/milestones", data)
    
    def create_issue(self, owner, repo, title, body=None, milestone_id=None, assignees=None, labels=None):
        """Create a repository issue."""
        data = {
            "title": title,
            "body": body
        }
        
        if milestone_id:
            data["milestone"] = milestone_id
        
        if assignees:
            # Ensure assignees is a list
            if isinstance(assignees, str):
                assignees = [assignees]
            data["assignees"] = assignees
        
        if labels:
            data["labels"] = labels
        
        return self._make_request("POST", f"/repos/{owner}/{repo}/issues", data)


def authenticate_github():
    """Authenticate to GitHub using a personal access token from environment variable."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set. Please set it with your GitHub personal access token.")
    
    try:
        github = GitHubAPI(token)
        # Test authentication by getting the authenticated user
        github.get_user()
        return github
    except Exception as e:
        raise ConnectionError(f"Failed to authenticate with GitHub: {e}")


def create_milestones(github, owner, repo, sprint_names, start_date=None):
    """Create sprint milestones with appropriate due dates."""
    if start_date is None:
        start_date = datetime.datetime.now()
    
    # Get existing milestones
    existing_milestones = github.get_milestones(owner, repo)
    existing_milestone_titles = {m["title"]: m for m in existing_milestones}
    
    milestones = {}
    
    for i, sprint_name in enumerate(sprint_names):
        # Calculate due date (one week per sprint from start date)
        due_date = start_date + timedelta(days=7 * (i + 1))
        
        if sprint_name in existing_milestone_titles:
            print(f"Milestone '{sprint_name}' already exists. Skipping creation.")
            milestone = existing_milestone_titles[sprint_name]
        else:
            milestone = github.create_milestone(
                owner=owner,
                repo=repo,
                title=sprint_name,
                description=f"Sprint {i+1} tasks",
                due_on=due_date
            )
            print(f"Created milestone: {sprint_name} (due: {due_date.strftime('%Y-%m-%d')})")
        
        milestones[i+1] = milestone
    
    return milestones


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
        print("Usage: python github_sprint_planner_rest.py <owner> <repo_name> <stories_json_file>")
        sys.exit(1)
    
    owner = sys.argv[1]
    repo_name = sys.argv[2]
    stories_file = sys.argv[3]
    
    try:
        # Authenticate to GitHub
        github = authenticate_github()
        
        # Verify repository exists
        github.get_repository(owner, repo_name)
        
        # Create sprint milestones
        sprint_names = ["Sprint 1", "Sprint 2"]
        milestones = create_milestones(github, owner, repo_name, sprint_names)
        
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
            try:
                issue = github.create_issue(
                    owner=owner,
                    repo=repo_name,
                    title=title,
                    body=description,
                    milestone_id=milestones[sprint_number]["number"],
                    assignees=[assignee] if assignee else None,
                    labels=labels
                )
                
                print(f"Created issue #{issue['number']}: {title}")
                issue_data.append([
                    issue['number'],
                    title,
                    assignee or "Unassigned",
                    f"Sprint {sprint_number}"
                ])
            except Exception as e:
                print(f"Error creating issue '{title}': {e}")
        
        # Print summary table
        print("\nSprint Planning Summary:")
        headers = ["Issue #", "Title", "Assignee", "Sprint"]
        print(tabulate(issue_data, headers=headers, tablefmt="grid"))
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 