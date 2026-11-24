---
title: How do you spot duplicate records in your customer relationship management (CRM) system?
primary_question: How do you spot duplicate records in your customer relationship management (CRM) system?
funnel_stage: TOFU
theme: duplicate records
campaign: 2026-Q3 Clean Customer Data
audience: Data leader
author: Sam Example, Head of Data Engineering
date: 2026-10-20
updated: 2026-10-20
original_angle: In our made-up sample of 5,000 contacts, 1 in 9 had a twin that differed by one character.
---

# How do you spot duplicate records in your customer relationship management (CRM) system?

You spot duplicate records by matching on more than one field. Compare email, company domain and a cleaned-up name together, then review the near matches by hand. Exact-match reports catch only the easy cases. Most duplicates differ by a typo, a nickname or a company suffix, so they hide from simple filters.

## What does a duplicate record look like?

A duplicate is two or more records that describe the same person or company. They usually differ in small ways: "Jon Smith" and "Jonathan Smith", or "Acme Inc." and "Acme Incorporated". Sales sees two contacts, marketing mails both, and reports count one buyer twice.

Common patterns include:

- The same email address with different capitalization or a plus tag.
- The same person at a new job, entered as a new contact.
- The same company under several spellings, entered by different teams.
- Records created by a form fill after a sales rep already added the contact by hand.

## Why do duplicates cause wrong reports?

Duplicates inflate counts and split history. One buyer shows up as two leads, so lead volume looks higher and conversion looks lower. Their activity is split across two records, so no single record shows the full story. A 2026 survey of operations teams from a made-up trade group reports similar effects: https://example.com/survey-2026.

## How do you find them without buying a tool first?

Start with a spreadsheet export and three passes. First, sort by lowercase email and flag repeats. Second, group by company domain and look for several spellings of the same name. Third, check contacts created within a day of each other, since form fills and manual entries often collide.

Here is a simple way to rank what to fix first:

| Check | Effort | What it catches |
|---|---|---|
| Same email, different case | Low | Obvious twins |
| Same domain, name variants | Medium | Company and contact splits |
| Created within one day | Medium | Form fill and manual entry collisions |

For a deeper walk-through of merging safely, see https://fernhill.example/blog/remove-duplicate-contacts and the matching guidance from a made-up standards group at https://example.com/matching-guide.

Fernhill Software built its checks around these same three passes, then added a review step so a person approves every merge. Teams that review near matches by hand avoid merging two different people by mistake, which is the costliest error to undo.

## Frequently asked questions

### How many duplicate records is normal?

There is no standard number. In our made-up sample, about 11 percent of contacts had a near twin. Treat any share above a few percent as worth cleaning, because the reporting error grows with every campaign.

### Should I merge duplicates automatically?

Merge exact matches automatically if you keep a backup. Send near matches to a person for review. A wrong merge is hard to undo, so the review step is worth the time.

### Who should own duplicate cleanup?

Revenue operations usually owns the rules, and each team owns the records it creates. Give one person the job of approving rule changes so the fixes stay consistent.

### How often should we check?

Run the three passes monthly, and after any large import or system change. Most new duplicates appear right after an import, an event list upload or a form change.
