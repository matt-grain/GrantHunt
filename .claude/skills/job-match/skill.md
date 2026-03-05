# Match Job Against Profile

Analyze a job posting and score it against your profile.

## Usage

```
/job-match <url>
```

## Instructions

1. Fetch and analyze the job posting:
   ```bash
   uv run jobhunt match "<url>"
   ```

2. Display the match results:
   - Overall score (0-100)
   - Breakdown by category
   - Red flags detected
   - Highlights found
   - Recommendation

3. Ask user if they want to add it to their tracker.

## Example Output

```
Job: Senior Engineering Manager at TechCorp
Score: 72/100

Breakdown:
  Role match: 85% (close to target titles)
  Tech focus: 70% (mentions AI, ML)
  Industry: 60% (B2B SaaS - neutral)
  Red flags: 75% (no major concerns)

Highlights:
  + "AI-first product development"
  + "Technical leadership"
  + "Hands-on when needed"

Red flags:
  ! "Some travel required"

Recommendation: Worth reviewing

Add to tracker? [y/n]
```

## Statuses

After adding, the job will have status NEW and can be updated with:
```bash
uv run jobhunt update <id> --status INTERESTED
```
