# GitHub Sprint Planning Automation

This project automates the process of creating sprints and user stories, similar to GitHub Issues.

## Options

This repository provides multiple implementation options:

1. **Token-free Local Simulation (Recommended)**:
   - Uses local file storage to simulate GitHub issues and milestones
   - Doesn't require GitHub authentication
   - Great for planning without actual GitHub integration

2. **GitHub API Integration**:
   - `github_sprint_planner.py` - Uses the PyGithub library
   - `github_sprint_planner_rest.py` - Uses direct REST API calls
   - Requires a GitHub personal access token with repo scope

## Prerequisites

- Python 3.6+
- For the GitHub API integration, a GitHub Personal Access Token with repo scope

## Installation

1. Clone this repository
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

### Token-free Local Simulation (Recommended)

This approach doesn't require GitHub authentication and simulates the creation of sprints and issues locally:

```bash
python github_sprint_planner_local.py <owner> <repo_name> <stories_json_file>
```

For example:
```bash
python github_sprint_planner_local.py "myusername" "my-mlops-project" user_stories.json
```

The results will be stored in the `local_github_simulation` directory, with separate subdirectories for milestones and issues.

To visualize the results in a more GitHub-like format:
```bash
python visualize_sprint_planning.py
```

### GitHub API Integration

If you want to create actual GitHub issues (requires a token):

1. Set your GitHub token as an environment variable:

```bash
# For Windows PowerShell
$env:GITHUB_TOKEN="your_token_here"

# For Bash/Linux
export GITHUB_TOKEN="your_token_here"
```

2. Run the script with your repository details:

```bash
# Using PyGithub library
python github_sprint_planner.py <owner> <repo_name> <stories_json_file>

# OR using direct REST API calls
python github_sprint_planner_rest.py <owner> <repo_name> <stories_json_file>
```

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
- `assignee`: Username of the assignee
- `labels`: Array of label names to apply
- `sprint`: Sprint number (1 or 2) (required)

## Features

- Creates two sprint milestones one week apart
- Creates issues for each user story
- Assigns issues to team members
- Applies labels to issues
- Groups issues under the appropriate sprint milestone
- Prints a summary table of all created issues 