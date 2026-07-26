# Financial Voice Pakistan — Enterprise AI FinTech Suite

Financial Voice Pakistan is a multi-page, voice-first personal ledger and enterprise financial analytics engine designed specifically for the Pakistani economic context. Built using Python and Streamlit, it integrates real-time multilingual speech parsing, local financial mechanisms (such as ROSCAs/Committees), household expense distribution, inflation-adjusted forecasting, and FBR-compliant tax computations into a single unified SQLite database architecture.

---

## Architecture Overview

The system follows a modular multi-page application structure built around a central database source of truth:

```text
FinancialVoicePakistan/
│
├── app/
│   ├── app.py                          # Primary Authentication & Page Router
│   └── pages/
│       ├── 01_Home_Dashboard.py        # Financial Pulse & Gauge Analytics
│       ├── 02_Voice_Entry.py           # NLP Voice Processing & Real-Time Verification
│       ├── 03_Personal_Insights.py     # AI Health Diagnosis & Conversational Assistant
│       ├── 04_Accountant_Mode.py       # Formal Income Statements (P&L) & Cash Flow
│       ├── 05_Budget_Tracker.py        # Category Budget Threshold Controls
│       ├── 06_Settings.py              # Security Passcode & Language Configurations
│       ├── 07_Committee_Simulator.py   # ROSCA Opportunity Cost & Ledger Synchronization
│       ├── 08_Household_Mode.py        # Family Member Expense Attribution
│       ├── 09_Inflation_Goal_Planner.py# Present vs Future Inflated Purchasing Power
│       ├── 10_Forecasting_Engine.py    # Time-Series Predictive Outflow Modeling
│       ├── 11_Report_Export.py         # Audit-Grade Document Generation & Export
│       ├── 12_Remittance_Tracker.py    # Foreign Exchange Conversion & Dependency Ratios
│       ├── 13_Smart_Tags_and_Duplicates.py # Duplicate Entry Audit & Hashtag Analytics
│       └── 14_Tax_Calculator.py        # FBR Pakistan Income Tax Computation Slabs
│
├── data/
│   └── finance.db                      # Central SQLite Source of Truth
│
├── src/
│   ├── database.py                     # Schema, Auto-Migrations & CRUD Functions
│   ├── voice.py                        # Multilingual Speech Transcription Engine
│   ├── parser.py                       # Transaction Entity Extractor
│   ├── analytics.py                    # Health Scoring & Financial Intelligence
│   └── translations.py                 # Regional Language Dictionaries
│
├── requirements.txt                    # Project Dependencies
└── README.md                           # Documentation