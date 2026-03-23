# Add Grant to Tracker

Add a grant opportunity to your grant tracking pipeline.

## Usage

```
/grant-add <url> [title] [organization]
```

## Instructions

1. Run the granthunt CLI to add the grant:
   ```bash
   uv run granthunt add "<url>" --title "<title>" --organization "<org>"
   ```

   Optional flags:
   ```bash
   --deadline YYYY-MM-DD       # Application deadline
   --amount-min X              # Minimum funding amount (CAD)
   --amount-max Y              # Maximum funding amount (CAD)
   --grant-type grant|tax_credit|loan
   ```

2. If title or organization are not provided by the user, ask for them before proceeding.

3. Report the result to the user, including the assigned grant ID.

## Example

```
/grant-add https://nrc.canada.ca/en/support-technology-innovation/about-nrc-irap "NRC IRAP" "National Research Council"
```

Full example with all flags:
```bash
uv run granthunt add "https://nrc.canada.ca/en/support-technology-innovation/about-nrc-irap" \
  --title "NRC IRAP" \
  --organization "National Research Council" \
  --deadline 2026-06-30 \
  --amount-min 50000 \
  --amount-max 500000 \
  --grant-type grant
```
