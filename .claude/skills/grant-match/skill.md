# Match Grant Against Profile

Analyze a grant opportunity and score it against the startup profile.

## Usage

```
/grant-match <url>
```

## Instructions

1. Fetch and analyze the grant opportunity:
   ```bash
   uv run granthunt match "<url>"
   ```

2. Display the match results:
   - Overall score (0-100)
   - Breakdown by scoring dimension
   - Red flags detected
   - Eligibility highlights
   - Recommendation

3. Ask the user if they want to add the grant to the tracker.

## Example Output

```
Grant: NRC IRAP — Industrial Research Assistance Program
Organization: National Research Council of Canada
Score: 84/100

Breakdown:
  Sector match:    90%  (cleantech / climate tech eligible)
  Eligibility:     85%  (Canadian SME, < 500 employees)
  Funding fit:     80%  (up to $500K non-dilutive)
  Keywords:        88%  ("net zero", "carbon reduction", "deep tech")
  Red flags:       75%  (matching contribution may be required)

Highlights:
  + Explicitly targets clean energy and net-zero technologies
  + Non-dilutive funding — no equity given up
  + Covers salaries, contractors, materials

Red flags:
  ! Matching contribution likely required (1:1 or 2:1)
  ! Must have a paying client or partner engaged

Recommendation: Strong match — worth applying

Add to tracker? [y/n]
```

## After Adding

Grant will have status DISCOVERED and can be progressed with:
```bash
uv run granthunt update <id> --status EVALUATING
```
