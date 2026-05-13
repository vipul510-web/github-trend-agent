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

## Scheduling (Mac cron — every 2 hours)

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
├── main.py              # entry point — orchestrates all monitors
├── github_monitor.py    # trending repos + hot issues
├── hn_monitor.py        # Hacker News GitHub mentions
├── email_sender.py      # Gmail SMTP email formatting + sending
├── state.json           # auto-created — tracks seen items
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
