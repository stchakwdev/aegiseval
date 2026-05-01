# Real-world knowledge-work eval expansion

Date: 2026-05-01

This note proposes AegisEval task additions grounded in live marketplace reconnaissance. The goal is to move beyond small deterministic MVP tasks into realistic freelance/analyst/operator work while preserving AegisEval's core properties: local-first reproducibility, inspectable artifacts, code-checkable outcomes where possible, and explicit audit trails.

## Sources checked

- Fiverr Market Research category: https://www.fiverr.com/categories/business/market-research-reports
- Fiverr Virtual Assistant category: https://www.fiverr.com/categories/business/virtual-assistant-services
- Fiverr Data category: https://www.fiverr.com/categories/data/data-analysis
- Upwork 2026 in-demand skills search results: https://www.upwork.com/research/in-demand-skills-2026
- Upwork data-analysis freelance jobs search result: https://www.upwork.com/freelance-jobs/data-analysis/

## Marketplace patterns observed

### Market research / business analysis

Observed Fiverr listings and category copy include:

- comprehensive market research for startup business
- business plans, SWOT analysis, strategic management, market research
- custom market research reports with actionable insights
- full comprehensive market research and business plan
- market research for startups and new businesses
- comprehensive market research, competitor analysis and business plan
- market research, SWOT and competitor analysis
- validating a business idea with market research and real customer feedback
- import/export shipment data for a product and HS code
- SEMrush/Ahrefs SEO competitor reports
- investor-ready business plan, market research and feasibility study

Fiverr category FAQ frames good market research as clarifying the client objective, choosing the right methodology, using qualitative and quantitative evidence, and producing insights for strategic and operational decisions.

### Virtual assistant / operations work

Observed Fiverr VA listings and category copy include:

- executive virtual assistant
- admin assistant and executive assistant
- data entry and web research
- social media manager / business operations assistant
- email and messaging support
- document formatting and template docs
- file conversion
- fact checking
- Google Maps/manual research
- ecommerce virtual assistant
- real estate skip tracing/property support
- mail merge for labels, letters, or envelopes

The category explicitly lists task families: General Assistance, Research Assistant, Messaging & Emailing, Template Docs & Formatting, File Conversion, Fact Checking.

### Data work

Fiverr's Data category describes:

- collecting, organizing, and analyzing business data
- understanding customers, competitors, and industry
- data analysis, data collection, data management, data science/ML
- data processing, mining, automation, web scraping, formulas, consultations
- Google/Excel sheets, statistical reports, BI/AI/big-data reports

Upwork search results also show data analysis, general virtual assistance, full stack development, graphic design, and AI-related work as in-demand in 2026.

## Task additions that would produce better signal

### 1. `market_research_brief_001`

**Real-world analogue:** Fiverr market research, competitor analysis, SWOT, startup business report.

**Scenario:** A founder wants a go/no-go brief for launching a niche product. Workspace contains:

- 3 competitor landing-page snippets
- 1 customer interview transcript
- 1 CSV of synthetic search/ad metrics
- 1 constraints memo from the founder

**Expected artifacts:**

- `brief.md`: executive summary, customer segments, competitor table, risks, recommendation
- `evidence.json`: structured claims with source ids

**Code grader:**

- Checks required sections exist.
- Checks competitor table includes all competitors.
- Checks recommendation is consistent with constraints and metrics.
- Checks every numeric claim in `brief.md` appears in `evidence.json` and traces to a fixture.

**Judge grader:**

- Scores insight quality, specificity, and whether the recommendation is actually decision-useful rather than generic.

**Failure modes to expose:**

- generic MBA-speak
- invented market facts
- unsupported TAM claims
- ignoring negative evidence
- shallow competitor analysis

### 2. `lead_list_enrichment_001`

**Real-world analogue:** contact list / prospect list building, web research, VA data entry.

**Scenario:** Given messy company records and snippets from fake company pages, produce a clean prospect CSV and short notes.

**Expected artifacts:**

- `leads.csv`: normalized company, domain, industry, role target, confidence, exclusion reason
- `notes.md`: assumptions and edge cases

**Code grader:**

- Checks schema, deduping, normalization, valid confidence range.
- Checks no excluded company appears in final leads.
- Checks ambiguous records are flagged rather than hallucinated.

**Judge grader:**

- Scores practical usefulness for a sales ops person: prioritization, conservative confidence, no fabricated contacts.

**Failure modes:**

- hallucinated emails
- duplicate leads
- wrong industry tags
- overconfident low-evidence enrichment

### 3. `executive_inbox_triage_001`

**Real-world analogue:** VA email/messaging support, executive assistant task prioritization.

**Scenario:** Workspace contains 25 synthetic emails/slack messages, calendar constraints, and a CEO preference memo.

**Expected artifacts:**

- `triage.json`: priority, owner, deadline, suggested action for each message
- `drafts.md`: 3 short draft replies
- `schedule.md`: proposed calendar changes

**Code grader:**

- Checks all message ids processed.
- Checks urgent compliance/customer items are P0/P1.
- Checks no impossible calendar overlaps.
- Checks drafts reference the correct facts.

**Judge grader:**

- Scores tone, judgment, and operational usefulness.

**Failure modes:**

- misses implicit deadlines
- over-prioritizes noisy messages
- makes scheduling conflicts
- writes verbose/unusable drafts

### 4. `seo_competitor_audit_001`

**Real-world analogue:** SEMrush/Ahrefs SEO competitor reports, market/competitor analysis.

**Scenario:** Provide exported synthetic SEO data: keywords, rankings, backlinks, page titles, traffic estimates.

**Expected artifacts:**

- `seo_audit.md`: competitor gaps, quick wins, content plan
- `keyword_plan.csv`: keyword, intent, difficulty, priority, target page

**Code grader:**

- Checks all high-opportunity keywords considered.
- Checks no banned/brand-only keywords recommended.
- Checks priority formula roughly matches traffic/difficulty constraints.

**Judge grader:**

- Scores strategic coherence and whether recommendations are actionable, not just a rephrased spreadsheet.

**Failure modes:**

- ignores search intent
- recommends impossible keywords
- overfits to volume and ignores difficulty
- generic SEO advice

### 5. `survey_analysis_report_001`

**Real-world analogue:** survey, Google Forms, market research reports.

**Scenario:** Synthetic survey CSV with Likert items, free-text responses, demographics, missingness, and deliberate contradictions.

**Expected artifacts:**

- `survey_report.md`: findings, caveats, segments, recommendation
- `analysis.json`: cleaned N, top themes, segment deltas, caveats

**Code grader:**

- Checks cleaned sample size, missingness, key percentages.
- Checks free-text themes against seeded labels.
- Checks limitations mention sampling bias.

**Judge grader:**

- Scores whether narrative avoids overclaiming and distinguishes signal from noise.

**Failure modes:**

- overclaims from biased sample
- misses contradictory free-text feedback
- wrong denominator after cleaning

### 6. `procurement_quote_comparison_001`

**Real-world analogue:** admin/operations assistant, business support, decision memo.

**Scenario:** Three vendor quotes with different pricing units, exclusions, service levels, and legal red flags.

**Expected artifacts:**

- `comparison.xlsx` or `comparison.csv`
- `recommendation.md`

**Code grader:**

- Checks normalized total cost calculation.
- Checks disqualifying terms are flagged.
- Checks recommendation matches weighted scoring rubric.

**Judge grader:**

- Scores usefulness to a manager and whether it highlights hidden risks.

**Failure modes:**

- compares monthly vs annual incorrectly
- ignores exclusions
- chooses cheapest despite disqualifying terms

### 7. `policy_update_diff_001`

**Real-world analogue:** compliance admin, document review, fact-checking.

**Scenario:** Old policy, new policy, email from legal, and employee FAQ draft.

**Expected artifacts:**

- `change_log.md`: material changes
- `faq.md`: corrected employee-facing FAQ
- `risks.json`: ambiguities/escalations

**Code grader:**

- Checks known material changes are captured.
- Checks FAQ does not contradict policy.
- Checks required escalations are present.

**Judge grader:**

- Scores clarity, tone, and whether risks are framed non-alarmistically.

**Failure modes:**

- misses subtle policy changes
- invents legal interpretations
- fails to escalate ambiguity

### 8. `customer_feedback_synthesis_001`

**Real-world analogue:** product/customer research assistant.

**Scenario:** Support tickets, app reviews, NPS comments, and roadmap constraints.

**Expected artifacts:**

- `themes.json`: themes, counts, severity, representative quotes
- `product_memo.md`: top 3 fixes, tradeoffs, roadmap recommendation

**Code grader:**

- Checks seeded issues are found.
- Checks quote ids are real.
- Checks recommendation respects roadmap constraints.

**Judge grader:**

- Scores product judgment and whether it separates high-frequency noise from high-severity issues.

**Failure modes:**

- cherry-picks quotes
- duplicates themes
- ignores severity
- invents user quotes

### 9. `real_estate_comp_report_001`

**Real-world analogue:** real estate comparable / ARV report, property research.

**Scenario:** Synthetic property facts, comparable sales table, inspection notes, and market adjustments.

**Expected artifacts:**

- `comp_report.md`
- `valuation.json`

**Code grader:**

- Checks comps filtered by distance/date/property type.
- Checks adjusted valuation calculation.
- Checks major repair caveats included.

**Judge grader:**

- Scores whether the report is conservative and investor-useful.

**Failure modes:**

- uses bad comps
- arithmetic mistakes
- ignores repair costs

### 10. `import_export_brief_001`

**Real-world analogue:** import/export shipment data and HS-code research.

**Scenario:** Product descriptions, synthetic shipment table, HS-code candidates, country restrictions.

**Expected artifacts:**

- `trade_brief.md`
- `hs_code_analysis.json`

**Code grader:**

- Checks HS code selected from valid candidates.
- Checks country restrictions and top suppliers are cited.
- Checks quantities/totals match data.

**Judge grader:**

- Scores risk framing and operational clarity.

**Failure modes:**

- wrong HS code
- ignores regulatory restriction
- fabricated supplier claims

## Judge design

AegisEval should not replace code graders with an LLM judge. The useful design is a **hybrid grader**:

1. Code grader enforces objective constraints.
2. Judge grader scores subjective quality dimensions.
3. Final score is a weighted composite.
4. Judge outputs are treated as evidence, not truth.
5. Judge disagreement/variance is tracked across judges and trials.

### Proposed judge dimensions

For each task, configure a rubric with dimensions such as:

- `factuality`: claims trace to provided files, no invented facts
- `completeness`: required deliverables and constraints handled
- `decision_usefulness`: output helps a real client make the next move
- `specificity`: concrete, quantified, non-generic
- `risk_awareness`: caveats, uncertainty, escalations
- `format_following`: artifact structure, schema, concise writing
- `professional_tone`: usable client-facing tone

### Proposed judge output schema

```json
{
  "score": 0.0,
  "passed": false,
  "dimensions": {
    "factuality": {"score": 0.0, "rationale": "..."},
    "decision_usefulness": {"score": 0.0, "rationale": "..."}
  },
  "critical_failures": ["fabricated citation"],
  "summary": "short explanation"
}
```

### Judge guardrails

- Use a held-out judge model different from the tested model where possible.
- Run at temperature 0.
- Require JSON output and apply the same hardened JSON parsing/repair adapter.
- Include only task instructions, fixture excerpts, artifact content, code-grader results, and rubric.
- Never let judge see the candidate model name by default, to reduce brand bias.
- Trace judge prompt hash, judge model id, raw JSON, and parsed score.
- Store judge result separately from code result: `judge_result.json`.
- Report calibration stats: judge-code disagreement, judge variance, average subjective score.

### Scoring formula

Default for hybrid tasks:

```text
final_score = min(code_score, 0.70 * code_score + 0.30 * judge_score)
passed = code_passed AND judge_score >= 0.70 AND no critical_failures
```

The `min` cap prevents an LLM judge from laundering objective failures.

## Implementation plan

### Phase 1: Add judge infrastructure

- Add `src/aegiseval/judge.py` with `JudgeConfig`, `JudgeResult`, and OpenAI-compatible judge client.
- Add `GraderSpec.kind == "hybrid"` execution path in `graders/registry.py`.
- Add `judge_result.json` and trace events:
  - `judge_request_started`
  - `judge_response_parse_failed`
  - `judge_result`
- Add CLI/suite flags:
  - `--judge-model`
  - `--judge-base-url`
  - `--judge-api-key-env`
  - `--judge-timeout`
  - `--no-judge`
- Preserve current code-only behavior as default for existing tasks.

### Phase 2: Add first realistic tasks

Prioritize these because they are highly representative and can be mostly code-graded:

1. `survey_analysis_report_001`
2. `executive_inbox_triage_001`
3. `market_research_brief_001`
4. `customer_feedback_synthesis_001`
5. `procurement_quote_comparison_001`

### Phase 3: Calibrate judge

- Run GLM 5.1, Kimi K2.6, DeepSeek V4 Pro on existing + new tasks.
- Judge with a held-out strong model.
- Manually review 10 disagreement cases.
- Tune rubric wording and dimension weights.

## High-value creative additions

### Adversarial client briefs

Real clients are ambiguous. Add tasks where the client asks for something slightly wrong:

- asks for TAM but fixtures only support SAM-like evidence
- asks to approve reimbursements but policy says deny
- asks for “top 20 leads” but only 12 meet quality threshold

Grade whether the model pushes back instead of fabricating compliance.

### Revision tasks

Many knowledge-work jobs are iterative. Add tasks where the model receives a flawed first draft and client feedback, then must revise without breaking correct parts.

Metrics:

- fixed requested issues
- did not regress previous correct facts
- kept artifacts consistent

### Multi-artifact consistency

Require a memo plus a JSON/CSV/spreadsheet. Grade cross-artifact consistency. This catches models that write a good narrative but produce bad structured artifacts.

### Time-budgeted triage

Give too many files and ask for a 30-minute triage deliverable. Grade prioritization and honest uncertainty. This tests realistic bounded attention.

### Human-review queue improvements

Queue examples by failure diversity, not just lowest score:

- one objective pass / judge fail
- one objective fail / judge pass
- one parse repair
- one flaky task pass and fail pair

## Next recommended build order

1. Implement hybrid judge scaffold, without turning it on for current tasks.
2. Add `survey_analysis_report_001` because it combines numeric correctness, synthesis, and overclaiming risk.
3. Add `executive_inbox_triage_001` because it tests operational judgment, prioritization, and tone.
4. Add `market_research_brief_001` because marketplace evidence says this is a common real freelance deliverable.
5. Run GLM 5.1, Kimi K2.6, DeepSeek V4 Pro with code-only + hybrid scoring and compare rank stability.
