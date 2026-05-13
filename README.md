# GitHub Trend Agent

Monitors GitHub trending repos, hot issues in those repos, and Hacker News discussions mentioning GitHub projects. Sends you an email digest whenever new high-traction items appear — so you can spot problems worth solving immediately.

## What it does

- **GitHub Trending**: scrapes daily trending repos (filters by configured languages/topics)
- **Hot Issues**: finds heavily-discussed open issues in those trending repos (signal for unsolved problems)
- **Hacker News**: polls HN Algolia API for recent GitHub-related stories with high score
- **Deduplication**: tracks seen items in `state.json` — only emails you about new things
- **Email**: sends a formatted HTML digest via Gmail SMTP

## Setup

```bash
cd github-trend-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Fill in .env with your credentials
```

## Configuration (.env)

| Variable | Description |
|---|---|
| `GMAIL_USER` | Your Gmail address |
| `GMAIL_APP_PASSWORD` | Gmail App Password (see below) |
| `TO_EMAIL` | Where to send alerts (can be same as GMAIL_USER) |
| `GITHUB_TOKEN` | GitHub personal access token (optional but recommended — raises rate limit from 60 to 5000 req/hr) |
| `LANGUAGES` | Comma-separated languages to filter trending repos (e.g. `Python,JavaScript`) — leave blank for all |
| `HN_MIN_SCORE` | Minimum HN score to include a story (default: 50) |
| `ISSUE_MIN_COMMENTS` | Min comments on a GitHub issue to include it (default: 5) |

### Gmail App Password

1. Go to your Google Account → Security → 2-Step Verification → App passwords
2. Create an app password for "Mail"
3. Paste the 16-character password into `GMAIL_APP_PASSWORD`

## Running manually

```bash
source .venv/bin/activate
python main.py
```

Add `--force` to send email even if nothing is new (useful for testing):

```bash
python main.py --force
```

## GitHub Actions (recommended — no Mac needed)

The workflow at `.github/workflows/trend-monitor.yml` runs every 3 hours automatically. State is committed back to the repo after each run so deduplication persists.

### 1. Add Secrets

Go to **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret name | Value |
|---|---|
| `GMAIL_USER` | `vipulagarwal.in@gmail.com` |
| `GMAIL_APP_PASSWORD` | Your Gmail app password |
| `TO_EMAIL` | `vipulagarwal.in@gmail.com` |
| `GH_PAT` | A GitHub personal access token (optional, raises rate limit) |

### 2. Add Variables (optional overrides)

Under **Settings → Secrets and variables → Actions → Variables**:

| Variable | Default |
|---|---|
| `LANGUAGES` | `Python,JavaScript,TypeScript` |
| `HN_MIN_SCORE` | `50` |
| `ISSUE_MIN_COMMENTS` | `5` |

### 3. Trigger manually to test

Go to **Actions → GitHub Trend Monitor → Run workflow** to fire it immediately and verify the email arrives.

## Scheduling (Mac cron — alternative)

```bash
crontab -e
```

Add this line (adjust path):

```
0 */2 * * * /Users/vipulagarwal/github-trend-agent/.venv/bin/python /Users/vipulagarwal/github-trend-agent/main.py >> /Users/vipulagarwal/github-trend-agent/agent.log 2>&1
```

## File structure

```
github-trend-agent/
├── .github/workflows/
│   └── trend-monitor.yml  # runs every 3 hours on GitHub Actions
├── main.py                # entry point — orchestrates all monitors
├── github_monitor.py      # trending repos + hot issues
├── hn_monitor.py          # Hacker News GitHub mentions
├── email_sender.py        # Gmail SMTP email formatting + sending
├── state.json             # committed by Actions bot — tracks seen items
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Costs

- **GitHub API**: free (unauthenticated: 60 req/hr, with token: 5000 req/hr)
- **HN Algolia API**: free, no auth
- **Gmail SMTP**: free
- **Total**: $0/run
