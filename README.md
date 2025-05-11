# MLOps Project Automation Tools

This repository contains automation tools for MLOps project management, including sprint planning and Git branch management.

## Tools Overview

### 1. Sprint Planning Automation

Tools for creating sprint milestones and user stories:

- `github_sprint_planner_local.py` - Token-free local simulation of GitHub Issues and Milestones
- `github_sprint_planner_rest.py` - Implements sprint planning using direct GitHub REST API calls
- `visualize_sprint_planning.py` - Visualizes locally created sprint data

### 2. Branch Management Automation

Tools for creating branch structure and protection rules:

- `github_branch_manager.py` - Creates dev/test branches and generates branch protection configurations
- `github_branch_manager_api.py` - Extended version that can apply branch protection rules via GitHub API

## Prerequisites

- Python 3.6+
- For GitHub API integration: A GitHub Personal Access Token with repo scope

## Installation

1. Clone this repository
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

### Sprint Planning

#### Token-free Local Simulation (Recommended)

This approach doesn't require GitHub authentication and simulates sprint planning locally:

```bash
python github_sprint_planner_local.py <owner> <repo_name> <stories_json_file>
```

For example:
```bash
python github_sprint_planner_local.py "myusername" "my-mlops-project" user_stories.json
```

To visualize the results:
```bash
python visualize_sprint_planning.py
```

#### GitHub API Integration

If you want to create actual GitHub issues (requires a token):

1. Set your GitHub token as an environment variable:

```bash
# For Windows PowerShell
$env:GITHUB_TOKEN="your_token_here"

# For Bash/Linux
export GITHUB_TOKEN="your_token_here"
```

2. Run the REST API script with your repository details:

```bash
python github_sprint_planner_rest.py <owner> <repo_name> <stories_json_file>
```

### Branch Management

#### Local Branch Creation and Protection Configuration

Create dev/test branches and generate branch protection configurations without applying them:

```bash
python github_branch_manager.py --owner <owner> --repo <repo_name>
```

Example:
```bash
python github_branch_manager.py --owner "myusername" --repo "my-mlops-project"
```

#### GitHub API Integration for Branch Protection

To create branches and apply protection rules via GitHub API (requires a token):

```bash
python github_branch_manager_api.py --owner <owner> --repo <repo_name> --token <token> --apply-protection
```

To check if branches are already protected:
```bash
python github_branch_manager_api.py --owner <owner> --repo <repo_name> --token <token> --check-protection
```

## Branch Structure

The branch management tools set up the following branch structure:

- `main` - Production environment (protected)
- `test` - Staging/testing environment (protected)
- `dev` - Development environment

Branch protection rules include:
- Required pull request reviews (at least 1 approving review)
- Required status checks (lint, unit-tests)
- Disabled force pushes and deletions

## JSON Format for User Stories

The sprint planning tools use the following JSON format for user stories:

```json
[
  {
    "title": "Story title",
    "description": "Detailed description",
    "assignee": "username",
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