# CURRENT_PACKAGE_AUDIT (pre-finishing package fossil_mortality_submission.zip)

## Consistency
- Title/abstract/main text: consistent; subtitle on doc title page was a
  layout subtitle, removed in Paleobiology build (title is the single line).
- Figure numbering: FIXED during finishing — fig_scheme.png was generated
  but never embedded/cited; now embedded as Figure 1 and cited "(Fig. 1)".
  Figures 1–7 all cited in text.
- Tables 1–3 all cited; Supplementary Table 1 cited in text.
- Equations: now numbered (1)–(8) at right margin (Paleobiology style);
  all remain native OMML.
- Numbers: every reported value is generated from result CSVs/JSONs at
  build time (verified: E[M_5]=14.6, E[M_100]=22.6, max-only median bias
  20.7 yr, iso-g max|Δg|=0.0119, Maiasaura median grid 0.01–6.6 yr,
  posterior-predictive p 0.99/0.92).
- References: converted Vancouver-numbered → Paleobiology author-date;
  all 14 entries verified/corrected via Crossref (see REFERENCE_AUDIT_FINAL).
- Stale files: old Vancouver-format docs (MAIN_MANUSCRIPT_inline.docx,
  COVER_LETTER.docx, SUPPLEMENT.docx) superseded by Paleobiology variants;
  removed from final ZIP.

## Journal-format deltas applied
- Author-date citations + alphabetical Literature Cited (unabbreviated
  journal names, hanging indent).
- Title page: bold title, author, RRH/LRH (≤50 chars).
- Abstract page: "Abstract.—", 208 words (≤300), author block italicized.
- Submission copy: TNR 12pt, double-spaced, continuous line numbers, US
  Letter, 1-inch margins; figures NOT embedded; tables + figure captions
  collected at end.
- Headings: primary centered bold, secondary flush-left; section numbers
  removed.
- Declarations added: Acknowledgments (AI-use), Author Contributions,
  Funding placeholder, Competing Interests, Data Availability.
- figures.pptx retained as ancillary editable file, not part of the
  submission ZIP's required set (kept in package for user convenience).
