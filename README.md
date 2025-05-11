# GitHub Sprint Planning Automation

This script automates the process of creating sprints and user stories in GitHub Issues.

## Prerequisites

- Python 3.6+
- GitHub Personal Access Token with repo scope

## Installation

1. Clone this repository
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

1. Set your GitHub token as an environment variable:

```bash
# For Windows PowerShell
$env:GITHUB_TOKEN="your_token_here"

# For Bash/Linux
export GITHUB_TOKEN="your_token_here"
```

2. Prepare your user stories JSON file (see `user_stories.json` for an example format)

3. Run the script with your repository details:

```bash
# Using PyGithub library
python github_sprint_planner.py <owner> <repo_name> <stories_json_file>

# OR using direct REST API calls
python github_sprint_planner_rest.py <owner> <repo_name> <stories_json_file>
```

For example:
```bash
python github_sprint_planner.py "myusername" "my-mlops-project" user_stories.json
```

## Implementation Options

This repository provides two implementation options:

1. `github_sprint_planner.py` - Uses the PyGithub library, which is a Python wrapper for the GitHub API
2. `github_sprint_planner_rest.py` - Uses direct REST API calls with the requests library

Both implementations provide the same functionality. Choose based on your preference or requirements.

## JSON Format

The user stories should be in the following format:

```json
[
  {
    "title": "Story title",
    "description": "Detailed description",
    "assignee": "github-username",
    "labels": ["label1", "label2"],
    "sprint": 1
  }
]
```

Where:
- `title`: The title of the issue (required)
- `description`: The detailed description for the issue body
- `assignee`: GitHub username of the assignee
- `labels`: Array of label names to apply
- `sprint`: Sprint number (1 or 2) (required)

## Features

- Creates two sprint milestones one week apart
- Creates GitHub issues for each user story
- Assigns issues to team members
- Applies labels to issues
- Groups issues under the appropriate sprint milestone
- Prints a summary table of all created issues 