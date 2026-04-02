# Report Standards — BloomBrain

These rules apply to **every report and analysis** produced. No exceptions.

---

## 0. Coverage Section (Required Header on Every Report)

Every report must open with:

| Field | Value |
|---|---|
| Target dataset size | |
| Actual scraped dataset size | |
| Coverage percentage | |
| What failed / was skipped | (and why) |

- **If coverage < 70%** → the report must explicitly state: ⚠️ *Reduced reliability — coverage below 70%.*

---

## 1. Source URLs

Source URLs must appear at the bottom of every report so every claim can be verified.

---

## 2. Finding Tags (Mandatory — Never Mix Without Labeling)

Every finding must be tagged:

- `SCRAPED` — hard data pulled directly from the scrape
- `INFERRED` — your interpretation of the scraped data
- `GENERATED` — based on general training knowledge (must always be flagged explicitly)

---

## 3. Confidence Levels

Every finding must include a confidence level: **high**, **medium**, or **low**.

Confidence is based on:
- % of dataset that mentions it
- Number of independent sources
- Coherence of signal (aligned vs. contradictory mentions)

### Confidence Level Guidelines

| Level | Criteria |
|---|---|
| **High** | ≥5% of dataset mentions it AND appears across multiple sources |
| **Medium** | 1–5% of dataset OR appears in only one source |
| **Low** | <1% of dataset |
| **Do not present as finding** | <0.5% — move to background context only |

### Sample Size Context

| Size | Label |
|---|---|
| <200 data points | Small sample |
| 200–500 data points | Moderate sample |
| 500+ data points | Strong sample |

**Always state the sample size next to any percentage.**

---

## 4. Quantify — Never Narrate

Not *"many women say X"* but *"23 out of 500 posts mention X (4.6%, strong sample)."*

Numbers, not adjectives. Always.

---

## 5. Insufficient Data Rule

If a claim cannot be backed up with data from the current scrape:
- State: **"Insufficient data."**
- Never guess.
- Never fill gaps with training knowledge without tagging it `GENERATED` and flagging it explicitly.

---

## 6. Devil's Advocate Section (Required)

Every report must include a devil's advocate section covering:
- Risks
- Counter-evidence
- Alternative interpretations
- Insufficient evidence flags

Challenge your own findings. Always.

---

## 7. Action Items — New Data Only

Action items must be based on **new data from the current reporting period only.**

Do not repeat previous recommendations unless supported by new signals from this scrape.

---

## 8. Temporal Stability Rule

A trend must appear in **at least 2 consecutive reporting periods** before being framed as structural.

Single-period signals must be labeled: *"Emerging signal — unconfirmed."*

---

*Last updated: 2026-03-15*
