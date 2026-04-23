# Requirements Summary

Source: input/TRP1 Challenge Week 10_ Conversion Engine for Sales Automation.md

## Core Objective
Build an automated lead generation and conversion system for Tenacious that:
- identifies synthetic prospects from public data
- qualifies using a grounded hiring-signal brief
- runs nurture outreach
- books discovery calls with clear context

## Implementation Requirements
- Production-ready code with clear project structure.
- Strong error handling and explicit failure behavior.
- Grounded claims only: do not over-claim beyond verifiable signals.
- Respect bench-to-brief constraints; do not commit unavailable capacity.

## Data and Safety Constraints
- Use public reproducible sources (Crunchbase, layoffs.fyi, public job posts, etc.).
- No real customer contact data.
- No fabricated case studies or unsupported outcomes.
- Preserve channel/policy constraints and challenge data handling rules.

## Scope Guardrails
- Keep features focused on required workflow.
- Avoid unnecessary additions that do not improve qualification, research quality, or booking flow.
