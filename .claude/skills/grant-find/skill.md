# Grant Discovery - Find Matching Opportunities

Discover grant opportunities using Chrome browser automation. Searches government portals and funding aggregators, extracts program listings, scores against the startup profile, and saves to prospects for later review.

## Prerequisites

**Requires Chrome connection.** If not connected:
```
/chrome
```
Or restart session with `claude --chrome`

## Usage

```
/grant-find [query] [--source <name>] [--all-sources]
```

Examples:
- `/grant-find` - Uses defaults from grant_profile.yaml, searches Innovation Canada
- `/grant-find "net zero SME Quebec"` - Search with specific query
- `/grant-find "cleantech" --source irap` - Search IRAP only
- `/grant-find "carbon reduction" --all-sources` - Search all enabled sources

## Instructions

### 1. Load Configuration

Read `grant_profile.yaml` for search criteria:
- Sector, eligibility attributes, target funding range, keywords

Read `grant_sources.yaml` for enabled sources:
- URL patterns, extraction approach, priorities

### 2. Determine Sources to Search

**Default:** Innovation Canada only (priority 1 — government aggregator with broadest coverage)

**With --source <name>:** Search specified source only
- `innovation_canada`, `irap`, `sdtc`, `sred`, `mei`, `investissement_quebec`, `pme_mtl`

**With --all-sources:** Search all enabled sources in priority order

### 3. For Each Source

#### 3a. Build Search URL

```python
# From grant_sources.yaml
url_template = source["search_url"]
url = url_template.format(
    query=urllib.parse.quote(search_query),
    sector=urllib.parse.quote(sector)
)
```

#### 3b. Navigate and Extract

Government sites use simpler HTML than job boards. Prefer `read_page` or `get_page_text` over JavaScript extraction — they are more reliable on gov.ca and canada.ca domains.

Use Chrome tools to:
1. Navigate to the search URL
2. Wait for the page to load fully (gov sites can be slow)
3. Use `read_page` to extract text content
4. Scroll if pagination exists; follow "Next" links for more results
5. Fall back to `javascript_tool` only if `read_page` returns insufficient data

#### 3c. Extract Grant Data

For each grant program found, extract:
- **title**: Grant/program name
- **organization**: Funding organization (e.g., "NRC", "SDTC", "Investissement Québec")
- **url**: Link to the program detail page
- **amount_min** / **amount_max**: Funding range if visible (CAD)
- **deadline**: Application deadline if shown
- **grant_type**: grant | tax_credit | loan | contribution
- **summary**: First 200 chars of program description

**Innovation Canada example (read_page):**
Navigate to `https://innovation.canada.ca/en/programs` and use `read_page` to extract the program list. Each program card typically contains the program name, organization, and a link.

**Individual program page detail:**
After collecting the list, visit 2-3 top candidates' detail pages for richer data (eligibility, amounts, deadlines).

### 4. Score Each Grant

Calculate a quick score based on `grant_profile.yaml`:

**Sector Match (40%):**
- Explicit cleantech / climate tech eligibility: 100%
- Broad tech/innovation eligibility: 60%
- Sector not mentioned or unclear: 30%
- Explicitly excluded sector: 0%

**Eligibility (30%):**
- All eligibility criteria clearly met (Canadian, SME, stage, province): 100%
- Most criteria met, minor uncertainty: 70%
- Key criterion unclear (e.g., employee count limit): 40%
- Likely ineligible: 0%

**Funding Fit (30%):**
- Amount range aligns with target in grant_profile.yaml: 100%
- Amount too small (< 25% of target): 40%
- Amount range unknown: 50%

### 5. Filter and Deduplicate

**Filter out:**
- Programs explicitly excluding the startup's sector
- Programs requiring a minimum employee count or revenue we don't meet
- Duplicate programs listed across multiple sources (match by program name + org)

**Deduplication:**
```python
seen = set()
unique_grants = []
for grant in all_grants:
    key = f"{grant.organization.lower()}|{grant.title.lower()[:40]}"
    if key not in seen:
        seen.add(key)
        unique_grants.append(grant)
```

### 6. Save to Prospects Database

```bash
uv run granthunt add-prospect "<url>" \
  --title "<title>" \
  --organization "<organization>" \
  --amount-min <amount_min> \
  --amount-max <amount_max> \
  --deadline <deadline> \
  --score <quick_score> \
  --source <source_name>
```

Prospects are deduplicated by URL — safe to re-run.

### 7. Present Summary

```
Grant Discovery Complete

Sources searched:
  - Innovation Canada: 18 programs found
  - IRAP: 3 programs found
  - SDTC: 5 programs found
  Total: 26 programs, 22 unique after deduplication

Top Matches (score >= 70):
#   Score  Title                                  Organization        Source
---------------------------------------------------------------------------
1   92     Industrial Research Assistance          NRC IRAP            irap
2   88     Sustainable Development Tech Fund       SDTC                sdtc
3   85     Green Transition Fund                   Investissement QC   innovation_canada
4   78     PME en action — Tech Propre             PME MTL             pme_mtl
5   72     SR&ED Tax Credit                        CRA                 sred

Filtered Out (ineligible or sector mismatch): 4 programs

Saved 22 prospects to review queue.
Run /grant-review to track or dismiss prospects.
```

## Source-Specific Notes

### Innovation Canada
- Primary aggregator: covers federal + some provincial programs
- Use as the default starting point
- Prefer `read_page` — the site is straightforward HTML

### NRC IRAP
- Non-dilutive, covers up to $500K for R&D staff and contractors
- Visit individual program pages for current deadlines and eligibility
- High-value target — always include

### SDTC (Sustainable Development Technology Canada)
- Focused on clean technology
- Larger grants ($1M–$5M range) — strong fit for later stages
- Uses `read_page` reliably on sdtc.ca

### SR&ED (Scientific Research & Experimental Development)
- Federal tax credit, not a grant — mark as `tax_credit`
- No deadline — annual claim with tax return
- Always eligible if doing R&D in Canada

### MEI (Ministère de l'Économie et de l'Innovation)
- Quebec provincial programs
- Some pages only in French — extract French text as-is, summarize in English

### Investissement Québec
- Quebec-focused, broader mandate than MEI
- Includes loans and equity; mark type accordingly

### PME MTL
- Montreal SME programs only
- Smaller amounts but fast turnaround
- Check eligibility for Montreal-based operations

## Error Handling

**If source fails to load:**
```
[!] MEI portal failed: timeout loading program list
    Continuing with other sources...
```

**If Chrome not connected:**
```
Chrome connection required for grant discovery.
Run /chrome to connect, or restart with: claude --chrome
```

**If CAPTCHA or login wall encountered:**
```
[source] requires login or verification. Please:
1. Complete the step in the browser
2. Say "continue" when ready
```

## Tips

- Innovation Canada alone covers 70%+ of relevant federal programs
- Government pages load slowly — allow 5-10 seconds before extracting
- Use `read_page` over JavaScript: gov sites are plain HTML, not SPAs
- Re-running is safe: prospects deduplicate by URL
- Check `grant_sources.yaml` to enable/disable sources per search
