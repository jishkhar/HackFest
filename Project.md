# Pocket CFO Agent - Project Blueprint

## 1. Project Summary

Pocket CFO Agent is a decision-first FinTech product for Indian GST-registered small and medium businesses. It is designed for owners who currently manage compliance, expenses, cash flow, taxes, and collections through disconnected tools such as basic bookkeeping apps, spreadsheets, SMS messages, WhatsApp or Telegram bills, bank statements, and manual CA workflows.

The core idea is simple: instead of waiting for the business owner to enter data and then showing passive dashboards, the system automatically ingests business events, normalizes them into an immutable ledger, runs specialized financial agents, and surfaces the next best decisions as action cards.

The product targets India's 63M+ GST-registered SMBs, especially businesses that need practical help with:

- GST compliance and input tax credit visibility.
- Expense classification and anomaly detection.
- Real-time profit understanding after GST, COGS, and fixed cost deductions.
- Cash-flow forecasting and shortfall warnings.
- Tax planning suggestions.
- Reconciliation between bank, UPI, invoices, and recorded ledger entries.
- Decision-making through simple action cards instead of complex dashboards.

## Document Map

- Sections 1-5 explain the product idea, problem, goals, and MVP scope.
- Sections 6-12 define the full architecture from ingestion to decision-first UI.
- Sections 13-14 describe the database model and API surface.
- Sections 15-18 show the project structure, development workflow, MVP demo, and GST Error Simulation.
- Sections 19-22 cover advanced features, security, and testing.
- Sections 23-30 explain setup, roadmap, backlog, risks, success metrics, and the recommended first build.

## 2. Source Deck Findings

The supplied PDF describes the project under:

- Team name: Team NPC (Not Paid Coders)
- College: Siddaganga Institute of Technology, Karnataka
- Track: FinTech
- Problem statement: India's GST-registered SMBs juggle compliance, expenses, cash flow, and taxes across disconnected tools, resulting in missed ITC, filing penalties, and no real-time financial clarity. Existing tools are passive and wait for owners to do the work.
- Product positioning: An autonomous "Pocket CFO Agent" that ingests data automatically and tells owners what to do next.

The PDF defines these major product pillars:

- Automatic ingestion from UPI/SMS, bank PDFs, invoice photos, Telegram bills, Excel, and voice.
- Six specialized AI/logic agents: GST, Expense, Profit, Cashflow, Tax, and Reconciliation.
- LangGraph orchestration with shared state.
- Deterministic GST rules for HSN/SAC lookup, GST slab classification, ITC checks, and filing draft generation.
- ML-backed expense classification and cash-flow forecasting.
- Decision-first mobile and web UI.
- MVP scope focused on UPI SMS ingestion, GST classification with ITC detection, three live action cards, and GST error simulation.

## 3. Problem Definition

### 3.1 Current SMB Pain Points

Indian SMB owners often operate with incomplete financial visibility because important business records are scattered across:

- UPI transaction SMS messages.
- Bank statements and bank PDFs.
- Invoice images and vendor bill photos.
- Telegram messages from vendors or customers.
- Excel sheets maintained by owners, employees, or accountants.
- Manual GST filing workflows.
- Verbal notes and memory-based bookkeeping.

This creates several recurring problems:

- Missed input tax credit due to untracked or incorrectly classified purchases.
- GST filing penalties because mistakes are noticed too late.
- Incorrect HSN/SAC or GST slab usage.
- Delayed collections from customers.
- Poor cash-flow visibility.
- No product-level profit clarity.
- No useful early warning when business risk increases.
- High dependency on owner discipline for bookkeeping.

### 3.2 Product Hypothesis

If the system can automatically capture business events from the tools SMBs already use, convert those events into structured ledger entries, and run compliance and finance agents continuously, then the owner can receive clear, timely action cards instead of passive reports.

### 3.3 Primary User Personas

#### Kirana Shop Owner

Needs fast entry, Hindi/English support, UPI and cash transaction tracking, inventory-aware purchase logging, and clear reminders for payments, dues, and GST.

Example:

> Owner says "Kal Rs 5,000 ka maal aaya" and the system creates a purchase entry, classifies it, and updates cash-flow impact.

#### Freelancer or Service Provider

Needs invoice scan, GST liability calculation, simple filing drafts, payment tracking, and expense categorization.

Example:

> Freelancer scans a vendor invoice and the system calculates GST treatment and prepares a GSTR-1 related entry.

#### Trader or Distributor

Needs receivable aging, vendor payable tracking, stock-related expense visibility, GST reconciliation, and pending collection alerts.

Example:

> System alerts "Rs 45,000 pending from 3 clients for 30+ days. Collect now."

#### Small Manufacturer

Needs true product-level profitability after raw material cost, GST, fixed costs, and overhead allocation.

Example:

> System identifies that one product line is loss-making after real cost and GST treatment.

#### CA Firm

Needs a multi-client console that reduces manual data cleaning and helps catch GST mismatches before filing.

Example:

> CA runs GST Error Simulation for all clients before filing deadlines.

## 4. Product Goals

### 4.1 Business Goals

- Reduce GST filing errors for SMBs.
- Help owners preserve cash by identifying collections, cash shortfalls, and avoidable purchases earlier.
- Make financial intelligence accessible without requiring accounting expertise.
- Build a SaaS product priced between Rs 499 and Rs 1,499 per business per month.
- Enable a B2B2B channel where CA firms pay per managed client.

### 4.2 Product Goals

- Minimize manual entry.
- Support how Indian SMBs already work: UPI SMS, Telegram bills, bank PDFs, voice, Excel, and invoice photos.
- Turn raw financial activity into structured ledger entries.
- Provide a decision-first home screen.
- Generate GST filing drafts and detect errors before filing.
- Forecast cash-flow issues up to 30 days ahead.
- Produce a business risk score useful for credit and loan workflows.

### 4.3 Engineering Goals

- Keep all normalized financial events traceable back to source evidence.
- Use an immutable double-entry ledger as the system of record.
- Separate deterministic compliance logic from probabilistic AI/ML predictions.
- Make each agent independently testable.
- Keep the MVP small enough to demo but architected for full product expansion.

## 5. Scope

### 5.1 MVP Scope From PDF

The PDF explicitly defines the MVP demo scope as:

- UPI SMS ingestion.
- GST classification agent with ITC detection.
- Decision-first home screen with three live action cards.
- GST Error Simulation.

### 5.2 Recommended MVP Scope

To make the MVP demo coherent, implement the following first:

- Manual or sample UPI SMS upload/input.
- SMS parser that extracts amount, direction, date, counterparty, and payment context.
- Basic merchant/vendor entity resolution.
- PostgreSQL ledger tables.
- GST classification service with deterministic rules.
- ITC eligibility detection for common categories.
- LangGraph workflow with a small shared state.
- Three action cards:
  - GST due or filing risk.
  - Cash-flow warning.
  - Pending collection or suspicious expense.
- GST Error Simulation screen with mock or rule-backed findings.

### 5.3 Post-MVP Scope

After the MVP, add:

- Invoice photo OCR.
- Telegram bill ingestion.
- Bank PDF parsing.
- Voice input with Hindi and English support.
- Prophet-based cash-flow forecasting using real history.
- Product-level profit engine.
- Tax planning agent.
- Reconciliation agent.
- CA firm multi-client portal.
- Loan-readiness and business risk score reports.

## 6. High-Level Architecture

The architecture from the PDF can be represented as five layers:

1. Data Ingestion
2. Normalization
3. Agent Orchestration
4. Synthesis
5. Decision-First UI

```text
Data Sources
    |
    v
Layer 1: Data Ingestion
    - UPI/SMS parser
    - Bank PDF parser
    - Invoice OCR
    - Telegram bill ingestion
    - Voice input
    - Excel import
    |
    v
Layer 2: Normalization
    - Deduplication
    - Entity resolution
    - Expense pre-classification
    - Ledger posting
    - Source evidence linking
    |
    v
Layer 3: Agent Orchestration
    - GST Compliance Agent
    - Expense Intelligence Agent
    - Profit Reality Agent
    - Cashflow Prediction Agent
    - Tax Planning Agent
    - Reconciliation Agent
    |
    v
Layer 4: Synthesis
    - Priority scorer
    - Alert deduplication
    - REST API gateway
    |
    v
Layer 5: Decision-First UI
    - React Native mobile app
    - Next.js web app
    - Action cards
    - Reports and drill-down views
```

## 7. Technology Stack

### 7.1 Frontend

- React Native for the mobile application.
- Next.js for the web application and CA/admin console.
- Shared design tokens and API client package where possible.

### 7.2 Backend

- Node.js API layer.
- Express or Fastify for REST endpoints.
- Python microservices for OCR, ML, forecasting, and agent workflows.
- LangGraph for multi-agent orchestration and shared workflow state.

### 7.3 Data and Storage

- PostgreSQL as primary database.
- Immutable double-entry ledger model.
- Redis for cache, deduplication windows, background job coordination, and priority queues.
- Object storage for invoices, bank PDFs, OCR source files, and evidence artifacts.

### 7.4 OCR and NLP

- Google Vision API for high-accuracy invoice extraction.
- Tesseract for fallback or local OCR.
- OpenAI Whisper for Hindi and English voice transcription.
- Rule-based extraction for predictable text patterns such as UPI SMS.

### 7.5 ML and Forecasting

- Fine-tuned expense classifier or BERT-based classifier for expense tagging.
- scikit-learn and Pandas for preprocessing, anomaly detection, and classification pipelines.
- Prophet and/or ARIMA for cash-flow forecasting.
- NumPy for forecasting and statistical calculations.

### 7.6 Compliance Logic

- Custom deterministic GST rules engine.
- HSN/SAC lookup table.
- GST slab classification.
- ITC eligibility rules.
- GSTR-1 and GSTR-3B draft generation.
- GST Error Simulation dry-run engine.

### 7.7 Integrations

- Telegram Bot API.
- UPI SMS parser.
- Bank PDF parser.
- GST portal APIs where access is available.
- Excel import.
- Optional accounting export for Tally/Zoho/Vyapar compatibility.

## 8. Layer 1: Data Ingestion

Layer 1 is responsible for collecting raw financial signals from real SMB workflows.

### 8.1 UPI/SMS Ingestion

Purpose:

- Capture UPI credit/debit events from SMS messages.
- Extract structured transaction records.

Inputs:

- SMS body.
- Sender ID.
- Received timestamp.
- User/business ID.

Extraction fields:

- Amount.
- Transaction direction: credit or debit.
- Counterparty name if present.
- UPI reference number.
- Bank account hint.
- Date/time.
- Balance if present.
- Payment mode.

Recommended implementation:

- Start with regex patterns for common Indian bank and UPI SMS formats.
- Use spaCy or a lightweight NLP pass for names and entities.
- Store raw SMS as source evidence.
- Attach parser confidence to every extracted field.

MVP example:

```text
Raw SMS:
Rs.5000 debited from A/c XX1234 to M/S SHREE TRADERS via UPI Ref 123456789 on 14-Apr.

Parsed event:
{
  "amount": 5000,
  "direction": "debit",
  "counterparty": "M/S SHREE TRADERS",
  "payment_mode": "UPI",
  "reference": "123456789",
  "source": "sms"
}
```

### 8.2 Bank PDF Ingestion

Purpose:

- Import bank statements where SMS history is incomplete.

Recommended tools:

- pdfplumber for table extraction.
- Layout analysis for banks with non-standard statement formats.

Output:

- Bank transactions normalized into the same raw event shape as SMS.

Important checks:

- Page-level extraction confidence.
- Duplicate detection against SMS records.
- Opening and closing balance consistency.
- Statement period validation.

### 8.3 Invoice OCR

Purpose:

- Extract vendor, buyer, GSTIN, invoice number, invoice date, taxable value, GST amount, line items, HSN/SAC codes, and total amount from invoice photos or PDFs.

Recommended tools:

- Google Vision API for primary OCR.
- Tesseract fallback.
- Invoice parser templates for common layouts.

Output:

- Invoice document.
- Invoice line items.
- GST summary.
- Source evidence image/PDF.

### 8.4 Telegram Bill Ingestion

Purpose:

- Support vendors who send bills directly on Telegram.

Flow:

- Business connects Telegram bot.
- Vendor bill images or PDFs are forwarded to the bot.
- Bot stores message metadata and file.
- OCR pipeline extracts invoice fields.
- Normalization pipeline links bill to vendor entity.

### 8.5 Voice Input

Purpose:

- Let SMB owners create financial entries through Hindi/English speech.

Example:

```text
"Kal Rs 2000 ka payment aaya"
```

Expected structured output:

```json
{
  "event_type": "payment_received",
  "amount": 2000,
  "date_text": "kal",
  "language": "hi-en",
  "confidence": 0.84
}
```

Implementation:

- Use Whisper for transcription.
- Resolve relative dates based on user timezone.
- Run an intent parser to classify the financial event.
- Ask for confirmation if confidence is low or important fields are missing.

### 8.6 Excel Import

Purpose:

- Help businesses migrate existing records.

Recommended support:

- Upload CSV/XLSX.
- Column mapping UI.
- Preview normalized entries.
- Reject rows with missing amount/date/type.
- Store original file as evidence.

## 9. Layer 2: Normalization

Normalization converts messy raw inputs into trusted, deduplicated, entity-linked financial records.

### 9.1 Deduplication

The PDF mentions deduplication using:

- Amount.
- Date.
- Party.
- Redis cache.

Recommended deduplication strategy:

- Generate an event fingerprint from source, amount, direction, date bucket, counterparty, and reference number.
- Use strict matching for transaction references.
- Use fuzzy matching for cases where bank statements and SMS have slightly different counterparty names.
- Maintain a deduplication status:
  - unique
  - probable_duplicate
  - confirmed_duplicate
  - conflicting_duplicate

Example fingerprint:

```text
business_id + date + amount + direction + normalized_counterparty + reference
```

### 9.2 Entity Resolution

Entity resolution maps aliases to known customers, vendors, banks, employees, or owners.

Examples:

- "SHREE TRADERS"
- "M/S SHREE TRADERS"
- "Shree Traders BLR"
- "SHREE TRADERS UPI"

All should resolve to one vendor entity when evidence is strong.

Entity model:

- Canonical name.
- Type: vendor, customer, bank, owner, employee, government, unknown.
- GSTIN.
- PAN if available.
- Phone/email.
- Aliases.
- Confidence score.

### 9.3 Expense Pre-Classification

The architecture slide refers to a BERT classifier for expense category pre-tagging.

Recommended categories:

- Inventory purchase.
- Rent.
- Utilities.
- Salaries/wages.
- Transport/freight.
- Marketing.
- Software/subscriptions.
- Professional fees.
- Bank charges.
- GST/tax payment.
- Owner withdrawal.
- Loan EMI.
- Miscellaneous.

Classification should return:

- Category.
- Confidence.
- Candidate GST treatment.
- ITC eligibility hint.
- Whether manual review is needed.

### 9.4 Ledger Posting

The database must use an immutable double-entry ledger. This ensures that every transaction balances and every edit is auditable.

Core principles:

- Ledger entries are append-only.
- Corrections are reversal or adjustment entries, not destructive updates.
- Every ledger entry has one or more debit lines and one or more credit lines.
- Total debit equals total credit.
- Every entry links back to source evidence.

Example purchase entry:

```text
Debit: Purchases / Inventory        Rs 5,000
Debit: Input GST Receivable         Rs   900
Credit: Bank Account                Rs 5,900
```

Example sales receipt:

```text
Debit: Bank Account                 Rs 11,800
Credit: Sales Revenue               Rs 10,000
Credit: Output GST Payable          Rs  1,800
```

## 10. Layer 3: Agent Orchestration

The PDF uses LangGraph for agent orchestration with shared state. This is a good fit because the product needs multiple specialized agents to run on the same normalized business context.

### 10.1 Shared Agent State

Shared state should contain:

- Business profile.
- Accounting period.
- New raw events.
- Normalized events.
- Ledger entries.
- Source documents.
- Entity graph.
- GST rule outputs.
- Agent findings.
- Forecasts.
- Action card candidates.
- Review queue items.

Example state shape:

```json
{
  "business_id": "biz_123",
  "period": {
    "start": "2026-04-01",
    "end": "2026-04-30"
  },
  "new_events": [],
  "ledger_entries": [],
  "agent_findings": [],
  "action_candidates": []
}
```

### 10.2 Agent Execution Model

Recommended execution pattern:

1. Ingestion creates or updates events.
2. Normalization posts trusted entries to the ledger or review queue.
3. LangGraph workflow runs all relevant agents.
4. Each agent emits findings with severity, confidence, evidence, and suggested action.
5. Synthesis layer deduplicates and prioritizes findings.
6. UI displays decision cards.

### 10.3 GST Compliance Agent

Responsibilities:

- HSN/SAC lookup.
- GST slab classification.
- ITC eligibility checks.
- Blocked credit detection.
- GSTR-1 draft generation.
- GSTR-3B draft generation.
- Mismatch detection before filing.
- GST Error Simulation.

Inputs:

- Sales ledger entries.
- Purchase ledger entries.
- Invoices.
- Vendor GSTIN.
- Buyer GSTIN.
- HSN/SAC rules.
- Filing period.

Outputs:

- GST liability estimate.
- ITC available.
- ITC blocked.
- Filing draft lines.
- Error simulation findings.
- High-priority action cards.

Example finding:

```json
{
  "agent": "gst_compliance",
  "severity": "red",
  "title": "Blocked ITC risk",
  "message": "Invoice INV-104 has GST claimed under a category that may not be eligible for ITC.",
  "suggested_action": "Review before filing GSTR-3B",
  "evidence_ids": ["invoice_INV_104"],
  "confidence": 0.91
}
```

### 10.4 Expense Intelligence Agent

Responsibilities:

- Multi-class expense classification.
- Rolling z-score anomaly detection.
- Expense trend detection.
- Vendor spend monitoring.
- Duplicate expense detection.

Inputs:

- Ledger expenses.
- Expense categories.
- Vendor entities.
- Historical spend patterns.

Outputs:

- Categorized expenses.
- Anomaly alerts.
- Review queue suggestions.
- Spend-saving opportunities.

Example finding:

```json
{
  "agent": "expense_intelligence",
  "severity": "amber",
  "title": "Transport expense unusually high",
  "message": "Transport expense is 42% above the recent weekly average.",
  "suggested_action": "Check freight bills before approving payment",
  "confidence": 0.77
}
```

### 10.5 Profit Reality Agent

Responsibilities:

- Calculate real profit per product, service, vendor, or business line.
- Include revenue, COGS, fixed costs, GST impact, and overhead allocation.
- Detect loss-making products.
- Support "what-if" profitability scenarios.

Inputs:

- Sales entries.
- Purchase entries.
- Product or service mapping.
- Fixed costs.
- GST treatment.
- Inventory or COGS mapping.

Outputs:

- Product-level gross margin.
- Net margin.
- Loss-making item alerts.
- Price increase recommendations.

Example action:

```text
Product A is losing money after GST and input cost. Raise price by 5% or renegotiate vendor cost.
```

### 10.6 Cashflow Prediction Agent

Responsibilities:

- Forecast liquidity for 7, 15, and 30 days.
- Predict cash shortfalls.
- Use ARIMA and/or Prophet on 90-day history.
- Account for known receivables and payables.

Inputs:

- Bank balances.
- UPI inflows/outflows.
- Receivables.
- Payables.
- Historical ledger.
- Expected GST/tax dues.

Outputs:

- Cash balance forecast.
- Shortfall warnings.
- Collection recommendations.
- Payment timing recommendations.

Example action:

```text
Cash deficit expected in 5 days. Collect Rs 32,000 pending dues before paying non-urgent purchase order.
```

### 10.7 Tax Planning Agent

Responsibilities:

- Estimate advance tax.
- Suggest deduction timing.
- Identify tax payment windows.
- Warn about tax cash-flow impact.

Inputs:

- Profit estimates.
- Prior tax payments.
- Current period revenue and expense.
- Applicable tax rules.

Outputs:

- Advance tax estimate.
- Suggested reserves.
- Deduction timing suggestions.
- Tax-related action cards.

### 10.8 Reconciliation Agent

Responsibilities:

- Match bank, UPI, invoices, and ledger entries.
- Detect missing invoices.
- Detect payments without corresponding invoices.
- Detect invoices without matching payment.
- Produce 3-way reconciliation report.

Inputs:

- Bank transactions.
- UPI/SMS transactions.
- Invoice records.
- Ledger entries.

Outputs:

- Matched records.
- Unmatched records.
- Mismatch findings.
- Reconciliation report.

Example finding:

```text
Payment of Rs 18,240 received from ABC Traders has no linked invoice. Create or link invoice before filing.
```

## 11. Layer 4: Synthesis

Layer 4 converts agent outputs into owner-friendly priorities.

### 11.1 Priority Scorer

The architecture slide defines:

- Red: act today.
- Amber: watch.
- Green: opportunity.

Recommended scoring factors:

- Compliance deadline proximity.
- Financial impact.
- Cash-flow impact.
- Penalty risk.
- Confidence score.
- Evidence quality.
- Whether the user can act immediately.
- Whether duplicate alerts exist.

Priority formula example:

```text
priority_score =
  deadline_weight +
  money_impact_weight +
  penalty_risk_weight +
  confidence_weight +
  actionability_weight -
  duplicate_penalty
```

### 11.2 Alert Deduplication

Multiple agents may create overlapping alerts. For example:

- GST Agent: GST payment due in 3 days.
- Cashflow Agent: cash deficit expected in 5 days.
- Tax Agent: reserve cash for tax payment.

The synthesis layer should merge related items into one better action:

```text
Pay Rs 18,240 GST in 3 days. Cash may fall short, so collect Rs 32,000 pending dues first.
```

### 11.3 REST API Gateway

The Node.js API gateway serializes outputs to frontend-friendly JSON.

Responsibilities:

- Authentication and authorization.
- Business and user context.
- Ingestion endpoints.
- Action card endpoints.
- Report endpoints.
- Review queue endpoints.
- Agent run triggers.
- Webhook endpoints.

## 12. Layer 5: Decision-First UI

The UI should avoid passive dashboard-first design. The home screen should answer:

> What should the business owner do next?

### 12.1 Mobile App

Primary user:

- SMB owner.

Primary screen:

- Action cards home screen.

Example cards from the deck:

- Pay Rs 18,240 GST - 3 days left.
- Cash deficit expected in 5 days.
- Collect Rs 32,000 pending dues.
- Profit down 12% this week.

Card requirements:

- Severity indicator: red, amber, or green.
- Plain-language action.
- Amount and deadline when available.
- One-tap drill-down.
- Evidence trail.
- Dismiss, snooze, or mark done.

### 12.2 Web App

Primary users:

- Business owner.
- Accountant.
- CA firm.

Recommended web sections:

- GST filing draft.
- GSTR-1 draft.
- GSTR-3B draft.
- GST Error Simulation.
- Profit breakdown by product line.
- What-if engine.
- Business risk score.
- 3-way reconciliation report.
- Review queue.
- Source documents.

### 12.3 Decision-First Copy Principles

Use owner-friendly language:

- "Collect Rs 32,000 from 3 clients this week."
- "Review invoice INV-104 before GST filing."
- "Cash may fall short on April 19."

Avoid accountant-heavy language in primary cards:

- "Section-level compliance anomaly detected."
- "Ledger variance exceeds configured threshold."

Detailed terminology can appear in drill-down screens for accountants.

## 13. Core Data Model

### 13.1 Main Entities

Recommended PostgreSQL tables:

- businesses
- users
- business_users
- entities
- entity_aliases
- source_documents
- raw_events
- normalized_events
- ledger_accounts
- ledger_entries
- ledger_lines
- invoices
- invoice_line_items
- gst_rules
- gst_classifications
- agent_runs
- agent_findings
- action_cards
- review_queue_items
- forecasts
- reconciliations
- audit_log

### 13.2 businesses

Stores business profile.

Important fields:

- id
- legal_name
- trade_name
- gstin
- pan
- state_code
- business_type
- filing_frequency
- created_at

### 13.3 source_documents

Stores raw evidence metadata.

Important fields:

- id
- business_id
- source_type: sms, bank_pdf, invoice_image, telegram, voice, excel
- storage_url
- raw_text
- checksum
- received_at
- uploaded_by
- parser_status

### 13.4 raw_events

Stores extracted but untrusted events.

Important fields:

- id
- business_id
- source_document_id
- event_type
- amount
- direction
- event_time
- counterparty_text
- reference_number
- raw_payload
- extraction_confidence
- status

### 13.5 normalized_events

Stores deduplicated, entity-linked events.

Important fields:

- id
- business_id
- raw_event_id
- entity_id
- event_type
- amount
- direction
- event_date
- category
- gst_treatment
- confidence
- dedupe_status
- review_required

### 13.6 ledger_entries

Stores immutable accounting events.

Important fields:

- id
- business_id
- normalized_event_id
- entry_date
- description
- status
- reversal_of_entry_id
- created_at
- created_by

### 13.7 ledger_lines

Stores debit and credit lines.

Important fields:

- id
- ledger_entry_id
- account_id
- debit_amount
- credit_amount
- entity_id
- tax_code
- product_id

Constraint:

- For every ledger entry, total debit must equal total credit.

### 13.8 agent_findings

Stores outputs from agents before synthesis.

Important fields:

- id
- business_id
- agent_name
- severity
- title
- message
- suggested_action
- money_impact
- deadline
- confidence
- evidence_json
- status

### 13.9 action_cards

Stores synthesized owner-facing actions.

Important fields:

- id
- business_id
- severity
- title
- body
- amount
- deadline
- action_type
- linked_finding_ids
- status: active, snoozed, dismissed, completed
- priority_score

## 14. API Design

### 14.1 Authentication

Recommended:

- JWT or session-based auth.
- Role-based access:
  - owner
  - staff
  - accountant
  - CA admin
  - platform admin

### 14.2 Ingestion APIs

```http
POST /api/businesses/:businessId/ingest/sms
POST /api/businesses/:businessId/ingest/invoice
POST /api/businesses/:businessId/ingest/bank-pdf
POST /api/businesses/:businessId/ingest/excel
POST /api/businesses/:businessId/ingest/voice
POST /api/integrations/telegram/webhook
```

### 14.3 Ledger APIs

```http
GET  /api/businesses/:businessId/ledger
GET  /api/businesses/:businessId/ledger/entries/:entryId
POST /api/businesses/:businessId/ledger/entries
POST /api/businesses/:businessId/ledger/entries/:entryId/reverse
```

### 14.4 Agent APIs

```http
POST /api/businesses/:businessId/agents/run
GET  /api/businesses/:businessId/agents/runs
GET  /api/businesses/:businessId/findings
```

### 14.5 Action Card APIs

```http
GET  /api/businesses/:businessId/action-cards
POST /api/businesses/:businessId/action-cards/:cardId/snooze
POST /api/businesses/:businessId/action-cards/:cardId/complete
POST /api/businesses/:businessId/action-cards/:cardId/dismiss
```

### 14.6 GST APIs

```http
GET  /api/businesses/:businessId/gst/summary
GET  /api/businesses/:businessId/gst/gstr-1-draft
GET  /api/businesses/:businessId/gst/gstr-3b-draft
POST /api/businesses/:businessId/gst/error-simulation
```

### 14.7 Report APIs

```http
GET /api/businesses/:businessId/reports/cashflow
GET /api/businesses/:businessId/reports/profit
GET /api/businesses/:businessId/reports/reconciliation
GET /api/businesses/:businessId/reports/risk-score
```

## 15. Project Repository Structure

Recommended monorepo structure:

```text
Pocket-CFO-Agent/
  apps/
    mobile/                 # React Native app
    web/                    # Next.js web app
    api/                    # Node.js API gateway
  services/
    agents/                 # Python LangGraph workflows
    ocr/                    # OCR extraction service
    forecasting/            # Prophet/ARIMA forecasting service
    classifiers/            # Expense classifier training/inference
    gst-rules/              # GST deterministic rules engine
  packages/
    shared-types/           # Shared TypeScript types
    api-client/             # Frontend API client
    config/                 # Shared lint/build config
  db/
    migrations/
    seeds/
    schema/
  docs/
    architecture/
    product/
    api/
  infra/
    docker/
    terraform/
  scripts/
  Project.md
  README.md
```

## 16. Development Workflow

### 16.1 Phase 0: Product and Technical Setup

Goal:

- Create the foundation for disciplined development.

Tasks:

- Finalize MVP user journey.
- Define sample businesses and sample financial records.
- Create repo structure.
- Set up Node.js API app.
- Set up Python services folder.
- Set up PostgreSQL and Redis through Docker Compose.
- Add migrations.
- Add linting, formatting, and test scripts.
- Create environment variable templates.

Deliverables:

- Running local stack.
- Database schema v1.
- Sample seed data.
- Health check endpoint.

### 16.2 Phase 1: UPI SMS Ingestion

Goal:

- Convert SMS text into normalized transaction events.

Tasks:

- Build SMS ingestion API.
- Implement parsers for 5-10 common SMS patterns.
- Extract amount, direction, date, counterparty, and reference.
- Store raw SMS as source document.
- Create raw_event records.
- Add parser confidence.
- Build tests with sample SMS messages.

Deliverables:

- SMS parser demo.
- Raw events created from sample SMS.
- Parser test suite.

### 16.3 Phase 2: Normalization and Ledger

Goal:

- Convert raw events into trusted ledger entries.

Tasks:

- Build deduplication service.
- Add entity resolution.
- Create ledger account chart.
- Create immutable double-entry ledger tables.
- Generate ledger entries for common events.
- Add review queue for low-confidence events.
- Add balancing constraints.

Deliverables:

- Deduplicated normalized events.
- Ledger entries with debit/credit lines.
- Review queue.

### 16.4 Phase 3: GST Rules Engine

Goal:

- Classify transactions for GST and ITC.

Tasks:

- Create HSN/SAC lookup model.
- Add GST slab rules.
- Add ITC eligibility rules.
- Implement GST classification API.
- Flag blocked ITC.
- Generate GSTR-1 draft lines for sales.
- Generate GSTR-3B draft summary.

Deliverables:

- GST classification service.
- ITC detection.
- GST summary endpoint.
- Unit tests for common GST cases.

### 16.5 Phase 4: LangGraph Agent MVP

Goal:

- Run the first agent workflow and produce findings.

Tasks:

- Set up Python LangGraph service.
- Define shared state schema.
- Implement GST Compliance Agent.
- Add simple Cashflow Agent using current balance and known upcoming GST due.
- Emit agent_findings.
- Store agent runs.
- Add API endpoint to trigger agent run.

Deliverables:

- Agent run endpoint.
- Stored findings.
- Traceable agent outputs.

### 16.6 Phase 5: Synthesis and Action Cards

Goal:

- Turn findings into owner-facing actions.

Tasks:

- Implement priority scoring.
- Implement alert deduplication.
- Create action_cards table.
- Generate red, amber, and green cards.
- Add card status changes: complete, snooze, dismiss.

Deliverables:

- Three live action cards.
- Action card API.
- Priority order validated against sample data.

### 16.7 Phase 6: Mobile Decision-First UI

Goal:

- Build the main owner experience.

Tasks:

- Create React Native app.
- Build login/business selection.
- Build action card home screen.
- Build action card detail screen.
- Show evidence and suggested action.
- Add complete/snooze/dismiss actions.

Deliverables:

- Mobile MVP demo.
- Live cards from backend.

### 16.8 Phase 7: GST Error Simulation

Goal:

- Let users dry-run GST filing before submission.

Tasks:

- Build simulation rules:
  - Missing HSN/SAC.
  - Wrong GST slab.
  - Blocked ITC claim.
  - Invoice/payment mismatch.
  - Missing vendor GSTIN.
  - Duplicate invoice number.
- Create simulation API.
- Build web/mobile simulation results screen.
- Link findings to evidence.

Deliverables:

- GST Error Simulation demo.
- List of fixable errors before filing.

### 16.9 Phase 8: Web Reports

Goal:

- Add accountant-friendly drill-downs.

Tasks:

- Create Next.js app.
- Add GST summary page.
- Add GSTR-1 draft page.
- Add GSTR-3B draft page.
- Add reconciliation report shell.
- Add profit breakdown shell.

Deliverables:

- Web demo with reports and drill-downs.

## 17. MVP Demo Script

The hackathon demo should be short and decision-oriented.

### 17.1 Demo Setup

Use a sample business:

- Name: Shree Lakshmi Traders
- GSTIN: sample/test GSTIN
- Business type: small trader
- Monthly sales: sample dataset
- Pending GST liability: Rs 18,240
- Pending receivables: Rs 32,000
- Upcoming cash shortfall: 5 days

### 17.2 Demo Flow

1. Show incoming UPI SMS sample.
2. Click ingest.
3. Show parsed transaction fields.
4. Show normalized ledger entry.
5. Run agents.
6. Show decision-first home screen.
7. Open GST card.
8. Run GST Error Simulation.
9. Show detected issue such as blocked ITC or wrong HSN/SAC.
10. Show how the owner can act immediately.

### 17.3 Demo Success Criteria

The audience should understand:

- The owner did not manually create a full accounting entry.
- The system turned raw financial text into a ledger event.
- The GST agent found a real compliance issue.
- The UI tells the owner what to do, not just what happened.

## 18. GST Error Simulation Design

### 18.1 Purpose

GST Error Simulation is a dry-run filing engine that catches mistakes before they become penalties.

### 18.2 Error Categories

Recommended simulation checks:

- Missing HSN/SAC code.
- HSN/SAC code mismatch with selected category.
- GST slab mismatch.
- ITC claimed on blocked category.
- Missing vendor GSTIN.
- Invoice number duplicate.
- Invoice date outside filing period.
- Purchase invoice exists but no payment evidence.
- Payment exists but invoice missing.
- Sales invoice missing from GSTR-1 draft.
- GSTR-1 and GSTR-3B taxable value mismatch.

### 18.3 Simulation Output

Each issue should include:

- Severity.
- Rule ID.
- Plain-language problem.
- Why it matters.
- Suggested fix.
- Evidence.
- Affected filing section.

Example:

```json
{
  "severity": "red",
  "rule_id": "ITC_BLOCKED_CATEGORY",
  "title": "Blocked ITC may be claimed",
  "why_it_matters": "This can create filing mismatch or penalty risk.",
  "suggested_fix": "Move this purchase to non-ITC expense or ask accountant to review.",
  "affected_document": "INV-104"
}
```

## 19. What-If Engine Design

The PDF mentions a What-If Engine for questions like:

- Raise price 5%?
- Delay this purchase 30 days?

### 19.1 What-If Inputs

- Price change percentage.
- Purchase delay.
- Customer payment delay.
- Vendor cost increase.
- GST payment timing.
- Expense reduction.

### 19.2 What-If Outputs

- Profit impact.
- Cash-flow impact.
- GST impact.
- Business risk score impact.
- Recommended decision.

Example:

```text
Raising price by 5% increases monthly gross profit by Rs 14,800 and reduces cash deficit risk from amber to green, assuming sales volume does not drop by more than 3%.
```

## 20. Business Risk Score

The PDF proposes a score from 0 to 100 based on financial and compliance signals.

### 20.1 Score Components

Recommended components:

- Cash-flow stability.
- GST filing streak.
- Expense volatility.
- Receivable aging.
- Profit margin trend.
- Reconciliation mismatch rate.
- Revenue concentration.
- Evidence completeness.

### 20.2 Example Weights

```text
Cash-flow stability:        25%
Compliance streak:          20%
Expense volatility:         15%
Receivable aging:           15%
Profit margin trend:        10%
Reconciliation quality:     10%
Evidence completeness:       5%
```

### 20.3 Score Output

Example:

```json
{
  "score": 74,
  "rating": "moderate",
  "main_risks": [
    "Receivables older than 30 days",
    "GST filing due in 3 days",
    "Transport expenses increased this week"
  ],
  "recommended_actions": [
    "Collect Rs 32,000 pending dues",
    "Review GST simulation errors before filing"
  ]
}
```

## 21. Security, Privacy, and Compliance

The project handles sensitive financial data, so security must be part of the architecture from day one.

### 21.1 Data Security

- Encrypt sensitive data at rest.
- Use TLS for all network traffic.
- Store source documents in private object storage.
- Use signed URLs for temporary document access.
- Redact secrets and financial identifiers from logs.

### 21.2 Access Control

- Role-based access control.
- Business-level tenant isolation.
- CA firm users can only access assigned clients.
- Staff roles can be limited to upload-only or view-only.

### 21.3 Auditability

- Every financial entry should link to source evidence.
- Every manual change should create an audit log entry.
- Ledger corrections should use reversal entries.
- Agent findings should store rule/model version.

### 21.4 AI Safety and Human Review

- Do not auto-file GST returns without explicit human approval.
- Low-confidence classification should go to review queue.
- Compliance logic should prefer deterministic rules over LLM-only reasoning.
- LLM-generated suggestions must be traceable and reviewable.

## 22. Testing Strategy

### 22.1 Unit Tests

Cover:

- SMS parser patterns.
- Amount/date extraction.
- Deduplication fingerprints.
- Ledger balancing.
- GST slab classification.
- ITC eligibility rules.
- Priority scoring.

### 22.2 Integration Tests

Cover:

- SMS ingestion to raw event.
- Raw event to normalized event.
- Normalized event to ledger entry.
- Ledger to GST finding.
- Finding to action card.

### 22.3 Golden Test Fixtures

Create fixtures for:

- Common UPI SMS messages.
- Bank statement rows.
- Invoice OCR samples.
- GST classification examples.
- Blocked ITC examples.
- Duplicate transaction scenarios.

### 22.4 Demo Acceptance Tests

The MVP should pass:

- Given a sample UPI SMS, the parser extracts correct fields.
- Given a purchase transaction, the GST agent classifies ITC eligibility.
- Given sample ledger data, action cards are generated.
- Given filing draft data, GST Error Simulation returns at least one meaningful finding.

## 23. Local Development Setup

### 23.1 Prerequisites

Recommended tools:

- Node.js 20+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker and Docker Compose
- pnpm or npm
- uv or pip for Python dependency management

### 23.2 Environment Variables

Example variables:

```text
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pocket_cfo
REDIS_URL=redis://localhost:6379
JWT_SECRET=local-dev-secret
GOOGLE_VISION_API_KEY=
OPENAI_API_KEY=
TELEGRAM_BOT_TOKEN=
OBJECT_STORAGE_BUCKET=
```

### 23.3 Suggested Startup Commands

Once the repo is scaffolded:

```bash
docker compose up -d postgres redis
pnpm install
pnpm db:migrate
pnpm db:seed
pnpm dev
```

Python services:

```bash
cd services/agents
uv sync
uv run python app.py
```

## 24. Implementation Roadmap

### 24.1 Week 1: Foundation

- Create monorepo.
- Configure API, database, and local Docker services.
- Define schema.
- Add seed data.
- Build health check.
- Create initial documentation.

### 24.2 Week 2: Ingestion and Ledger

- Build SMS ingestion.
- Implement parser tests.
- Implement normalization.
- Implement basic entity resolution.
- Create ledger entries.
- Add review queue.

### 24.3 Week 3: GST MVP

- Implement GST rules engine.
- Add ITC checks.
- Generate GST summary.
- Add GSTR draft data model.
- Add GST Error Simulation v1.

### 24.4 Week 4: Agents and Action Cards

- Add LangGraph service.
- Implement GST Compliance Agent.
- Add simple Cashflow Agent.
- Implement priority scorer.
- Generate action cards.
- Connect backend APIs.

### 24.5 Week 5: Mobile Demo

- Build React Native app.
- Add action card home screen.
- Add card details.
- Add GST simulation screen.
- Polish demo data and flow.

### 24.6 Week 6: Web and Advanced Demo

- Build Next.js web shell.
- Add GST reports.
- Add reconciliation report placeholder.
- Add profit breakdown placeholder.
- Prepare pitch-ready demo.

## 25. Backlog

### 25.1 Must Have

- SMS ingestion.
- Immutable ledger.
- GST classification.
- ITC detection.
- LangGraph agent workflow.
- Action cards.
- GST Error Simulation.
- Mobile action-card UI.

### 25.2 Should Have

- Invoice OCR.
- Telegram ingestion.
- Bank PDF ingestion.
- Web GST reports.
- Basic reconciliation.
- Cash-flow forecasting.

### 25.3 Could Have

- Voice input.
- Product-level profit engine.
- What-if simulations.
- Business risk score.
- CA firm dashboard.
- Loan-readiness report.

### 25.4 Later

- Live GST portal integration.
- Tally/Zoho/Vyapar import/export.
- Multi-language UI.
- Automated vendor/customer reminders.
- Embedded credit marketplace.

## 26. Key Engineering Risks

### 26.1 GST Rule Accuracy

Risk:

- Incorrect GST logic can create user harm.

Mitigation:

- Keep rule engine deterministic.
- Version all rules.
- Add test fixtures.
- Require accountant review before filing.

### 26.2 OCR Reliability

Risk:

- Invoice photos can be noisy, incomplete, or handwritten.

Mitigation:

- Store OCR confidence.
- Send low-confidence documents to review queue.
- Use templates for common invoice layouts.
- Keep original source evidence.

### 26.3 Duplicate Transactions

Risk:

- Same transaction may come from SMS, bank PDF, Telegram, and invoice.

Mitigation:

- Use reference numbers where available.
- Use fuzzy matching.
- Keep duplicate status and manual review.

### 26.4 Agent Trust

Risk:

- Users may not trust AI recommendations.

Mitigation:

- Every action card should explain evidence.
- Use deterministic rules for compliance.
- Show confidence and allow review.
- Keep language practical and non-alarming.

### 26.5 Data Privacy

Risk:

- Financial data is sensitive.

Mitigation:

- Strong tenant isolation.
- Encryption.
- Least-privilege access.
- Audit logs.
- Redacted logs.

## 27. Success Metrics

### 27.1 Product Metrics

- Percentage of transactions auto-ingested.
- Percentage of transactions classified without manual correction.
- Number of GST errors caught before filing.
- Number of action cards completed.
- Reduction in overdue receivables.
- User retention by business type.

### 27.2 Engineering Metrics

- Parser accuracy.
- OCR field extraction accuracy.
- Ledger balancing errors.
- Agent run latency.
- Action card precision.
- False positive rate for GST simulation.

### 27.3 Business Metrics

- Monthly recurring revenue.
- Conversion from trial to paid.
- Average revenue per business.
- CA firm clients onboarded.
- Churn rate.

## 28. Recommended First Build

Start with the smallest flow that proves the product thesis:

```text
UPI SMS -> Parser -> Normalization -> Ledger -> GST Agent -> Action Cards -> GST Error Simulation
```

### 28.1 Build Order

1. Create database schema.
2. Create API service.
3. Add sample business.
4. Add SMS ingestion endpoint.
5. Parse SMS into raw event.
6. Normalize event and resolve party.
7. Post ledger entry.
8. Run GST classification.
9. Generate GST finding.
10. Generate action cards.
11. Build mobile home screen.
12. Build GST simulation screen.

### 28.2 First Demo Dataset

Create 10-20 sample events:

- 5 UPI sales receipts.
- 4 vendor purchases.
- 2 expenses.
- 2 customer receivables.
- 1 GST payment due.
- 1 invoice with wrong GST slab.
- 1 invoice with blocked ITC.
- 1 duplicate transaction.

### 28.3 First Action Cards

For the MVP, generate:

```text
Red: Pay Rs 18,240 GST - 3 days left.
Amber: Cash deficit expected in 5 days.
Green: Collect Rs 32,000 pending dues.
```

These match the decision-first direction shown in the architecture slide.

## 29. Definition of Done for MVP

The MVP is done when:

- A user can submit sample UPI SMS text.
- The backend extracts key transaction fields.
- The system stores raw evidence.
- The event is normalized and deduplicated.
- A valid ledger entry is created.
- GST classification and ITC detection run.
- LangGraph workflow creates findings.
- Synthesis creates at least three action cards.
- Mobile or web UI displays action cards.
- GST Error Simulation identifies at least two filing risks.
- Every action card links back to source evidence or computed reasoning.

## 30. Final Product Vision

Pocket CFO Agent should become an autonomous financial operating layer for Indian SMBs. The final product should not feel like another accounting dashboard. It should feel like a practical finance assistant that watches incoming business activity, keeps the books clean, catches GST issues before penalties, warns about cash-flow pressure, and tells the owner what to do next.

The strongest version of this project combines:

- Automatic data capture.
- Deterministic compliance rules.
- Immutable accounting records.
- Specialized AI agents.
- Clear owner-first decisions.
- Accountant-grade drill-downs.

That combination is what differentiates it from passive tools such as Tally, Vyapar, and Zoho.
