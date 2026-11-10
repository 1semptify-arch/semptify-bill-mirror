# Voice Board — Moderation Standard

The public version of this standard is published on `/your-voice` ("The
review standard"). This file is the working rubric for whoever moderates —
Brad, an agent, or a future community moderator. If the public text and this
rubric ever disagree, the public text wins; fix this file.

## The line (Brad, 2026-11-10)

Moderation protects people. It never protects the bill from criticism.
Constructive criticism — including harsh criticism of the bill, the math,
the politics, or the people writing it — is the point of the board. We
cannot grow if we are unwilling to hear every viewpoint.

Hate, bigotry, racism, antisemitism — there is no place for that. That is
fear coming out sideways, not a viewpoint. It gets removed, always.

**When in doubt: publish and answer. The bias is toward hearing it, not
hiding it.**

## Decision table

| Post contains | Action |
|---|---|
| Names, addresses, case details, identifying info | Strip the details, publish the rest (Polis-style redaction — sentiment survives) |
| Threats, harassment, doxxing | Decline |
| Hate/bigotry targeting a group (racism, antisemitism, etc.) | Decline |
| Spam, ads, repeated junk, gibberish | Decline |
| Illegal content | Decline |
| Impersonation (claims to be a named person/org untruthfully) | Decline |
| Opinion on the bill — support, criticism, hostile tone but about the issue | **Publish.** Answer in the open if we can |
| Question | Publish; answer when possible, labeled by role |
| False or misleading claim about the bill/facts | Publish; correct it publicly in the answer — do not delete for being wrong |

Notes:

- Posts are anonymous by design, so "personal attack" almost always means
  an attack on a group or an identifiable public figure — the hate row
  governs. Criticism of the bill's *authors* as public actors is opinion;
  slurs and dehumanizing language are hate.
- Harsh tone alone is not a decline reason. A post that says "this bill is
  a scam and here's why" stays up. A post that says "kill all landlords"
  does not.
- Unverifiable claims get answered with the public record (the draft text,
  the research page), not silently removed — corrections are posted in the
  open, same as everything else on this site.

## How moderation runs today

- Intended path: `/admin/public-voice` → publish / answer / decline /
  unpublish. (Admin lane is currently excluded from the `render_mvp`
  production build — see OPERATIONS_LOG.)
- Interim path until the admin lane ships: direct `voice_posts` update in
  the Neon `semptifty_db` database — `status` + `is_published` per the
  decision table. The public API (`GET /api/voice-posts`) reads
  `is_published`; `awaiting_review` counts unpublished rows including
  declined ones (known cosmetic bug).
- Every moderation action should be deliberate and logged here or in
  OPERATIONS_LOG — no silent deletes.

## Toward public-driven review

The published standard is only half of "driven by the public." The full
version adds a **flag/report** control on each board post so readers
surface problems themselves, feeding the same review queue. Tracked as a
staged feature — app-side change, not yet built.
