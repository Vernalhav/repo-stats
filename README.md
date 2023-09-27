# Repo stats
Basic dashboard for displaying GitHub PR metrics. The metrics that are currently displayed 
in the dashboard are the average number of files changed per PR and the number of hotfixes
per release.

## Screenshots
![image](https://github.com/Vernalhav/repo-stats/assets/40337396/92cd4671-b2fd-4053-90fa-6038cdb17ade)

## Installation
After creating and activating a virtual environment, run
```bash
pip install -r requirements.txt
pip install .
```
To install dev dependencies, run
```bash
pip install -r requirements.dev.txt
```

## Usage
The program contains 3 separate CLIs, described below. To use the main CLI and the Metrics CLI, you must have
an environment variable called `GITHUB_TOKEN` containing a Personal Access Token to the GitHub API. If a `.env`
file is at the current working directory, it will be loaded.

### Main CLI
Downloads metrics and runs dashboard server.
```bash
# To view arguments
python3 -m repostats -h

# Usage example
python3 -m repostats -p 8000 --max-prs 60 vernalhav/repo-stats thebricks/mirroredsouls
```

### Metrics CLI
Downloads metrics to specified JSON file
```bash
# To view arguments
python3 -m repostats.metrics -h

# Usage example
python3 -m repostats.metrics -o metrics.json --max-prs 60 vernalhav/repo-stats thebricks/mirroredsouls
```

Example of a single PR metric:
```json
{
    "repo": "theBricks/MirroredSouls",
    "head_ref": "fix/invisible-platforms",
    "base_ref": "develop",
    "created_at": "2023-08-30T23:25:57Z",
    "merged_at": "2023-09-01T02:04:47Z",
    "state": "MERGED",
    "changed_files": 12
}
```

### Dasboard CLI
Runs dashboard with metrics from specified JSON file
```bash
# To view arguments
python3 -m repostats.dashboard -h

# Usage example
python3 -m repostats.dashboard -p 8000 metrics.json
```
