# Terminology policy

Single owner of the keep-English / write-Persian split.
`scientific-style.md` owns register and orthography, `glossary.md` holds
the house lists (document chrome, keep-English classes, recurring
infrastructure nouns), and `term-pairs.tsv` is the machine-readable half
that `scripts/check-fa.py` enforces. Do not restate this policy anywhere
else.

There is no per-field glossary in this skill. Infer the **jobs** and the
**subjects** from the source in hand. Counts are not fixed — choose how
many of each the source needs. Do not look up a pack name, and do not
write terms into `glossary.md`.

## Level

Two levels, because a sysadmin install guide and a journal paper cannot take
the same treatment. Announce the level in the first chat message.

| Level | For | Job lexicon (one-word field nouns) |
| --- | --- | --- |
| `system-docs` (default) | books, install guides, protocol specs, product docs, RFC/BIP, runbooks | English (`deployment`, `upstream`, `configure`) |
| `journal` | papers, theses, review articles for a general scientific audience | Persian, unless the token is in the subject lexicon |

The **subject** lexicon (products, protocols, tools the document is about)
stays English at both levels. The level only moves the boundary for the
**job** lexicon — ordinary one-word terms of the practice — and their
operation verbs. The user switches with «سطح journal» or «سطح system-docs».

### Audience (do not collapse these)

- **`system-docs`.** Write for practitioners who already live in the
  English tooling lexicon. Prefer the community designation (`deployment`,
  `source code`, `request`) over Academy neologisms that specialists do
  not actually use. Unfamiliar coined Persian that forces the reader to
  re-translate mentally is a terminology failure, not a patriotic success.
- **`journal`.** Write for a general scientific reader. Where a Persian
  designation is **stable and familiar** in that discipline (and not a
  house-forbidden calque for a kept subject term), prefer Persian and
  gloss the English once on first mention. Where the Academy form is
  unused or ambiguous in the field, keep English — familiarity beats
  novelty. Subject-lexicon tokens stay English at this level too.

Announce level, jobs, subjects, and **genre** (`tutorial`, `reference`,
`paper`) with the first terminology message. Genre only shifts tone
(`scientific-style.md`); it does not move the keep-English boundary.

## Concept-oriented `terms.tsv`

Before drafting, lock designations in a working-tree `terms.tsv`
(`long-documents.md`). Treat it as a **concept entry list**, not a flat
word dump (ISO 704 / ISO 12616 practice, simplified for one job):

| Column | Required | Meaning |
| --- | --- | --- |
| `source` | yes | English (or source-language) designation as it appears |
| `output` | yes | Form that must appear in the translation |
| `step` | yes | Decision step / reason (`subject-lexicon`, `job-lexicon`, `prose`, `chrome`, …) |
| `count` | yes | Rough occurrence count in the source |
| `forbidden_fa` | yes on keep-English rows | Persian calque that must never replace `output` |
| `concept` | recommended | Short concept id shared by synonyms (`cfg-deploy`, `src-code`) |
| `status` | recommended | `preferred` (default), `admitted`, or `deprecated` |
| `admitted` | no | Pipe-separated alternate OK forms |
| `deprecated` | no | Pipe-separated extra forms to avoid (checker also forbids these) |

Rules:

- One **preferred** designation per `concept` for the whole document.
- Keep-English preferred rows must set `forbidden_fa` (and usually list
  further junk forms in `deprecated`).
- Persian-output prose/chrome rows leave `forbidden_fa` empty.
- Never half-translate a concept. Never write two preferred forms for
  one concept.
- Discard `terms.tsv` with the job; do not merge it into `glossary.md`.

Example:

```text
source	output	step	count	forbidden_fa	concept	status	admitted	deprecated
source code	source code	3 job-lexicon	12	کد منبع	src-code	preferred		کد مبدأ|کد اصلی
deployment	deployment	3 job-lexicon	22	استقرار	cfg-deploy	preferred		
location	location	3 subject-lexicon	84	مکان	ngx-location	preferred		
security	امنیت	5 prose	41		sec-generic	preferred		
Introduction	مقدمه	0 chrome	1		chrome-intro	preferred		
```

## Infer jobs and subjects

Before classifying tokens, read enough of the source to name these, and
announce them with the level. **Counts are not fixed** — choose how many
jobs and how many subjects the source needs; do not pad to three and do
not force a single subject when the document is clearly about more than
one product.

- **Jobs** — one or more short practice labels, ranked by how much of the
  source they cover (`software development`, `DevOps`, `networking`,
  `Linux`, …). Include a broader practice when it supplies lexicon the
  narrower ops labels miss (e.g. `software development` so `source code`
  stays English in a Kubernetes book). Each label must be a real thread
  in the source (a chapter, audience, or repeated terms of art). Do not
  invent a practice the source does not use. The **job lexicon** is the
  union of the jobs you named.
- **Subjects** — one or more products, protocols, tools, or corpora the
  document is about (`nginx`, `Kubernetes`, `Helm`, Bitcoin, ImageNet,
  …). When two tools are co-equal topics, name both; when everything
  orbits one product, name one. The **subject lexicon** is the union of
  those subjects.

Those names are not pack ids and are not looked up in this repository.
Example: jobs `software development`, `DevOps`; subjects `Kubernetes`,
`Helm`; level `system-docs`.

Then every term that belongs to that job lexicon **or** that subject
lexicon stays English: directives, modules, CLI flags, config keys,
named blocks, operation verbs of those terms, and multi-word labels in
that lexicon.

A token belongs to the inferred lexicon when at least one of these holds:

- it is a name, directive, module, flag, API, or config key of a named
  subject (`nginx`, `location`, `proxy_pass`, `worker_processes`);
- it is a term of art of one of the named jobs as this document uses it
  (the field-term test below);
- it appears in the source's own glossary, or in a named subject's man
  page, `--help`, or spec index.

It does **not** belong when it is ordinary dictionary use in a sentence
about something else. In an nginx book, `location` as a block directive
stays English; «if the file is missing» is ordinary prose (فایل / پرونده).
In «increase security using firewalls», `security` is امنیت and
`firewalls` stays English.

Do not append rows to `glossary.md`. Do not create `glossary.local.md`.
Lock the choices in the working tree as `terms.tsv` (`long-documents.md`)
and discard that file with the job.

## Decision procedure

Ordered. First match wins. Apply to each source token or noun phrase.

0. **Document chrome.** A generic IMRAD or book label — `Abstract`,
   `Introduction`, `Methods`, `Results`, `Discussion`, `Conclusion`,
   `References`, `Figure`, `Table`, `Equation`, `Section`, `Appendix`,
   `Contents` / `Table of contents` / `Brief contents`, `Foreword`,
   `Preface` — is Persian, always, at every level. This step exists so a
   source glossary cannot drag `Introduction` into English. It applies
   only to the bare label, never to a heading that names an artifact. A
   book contents page is translated and printed; omitting it is a missing
   section, not a layout choice.
1. **Named artifact.** Product, project, algorithm, library, protocol,
   standard, opcode, identifier, acronym, unit, statistical symbol,
   person, journal, conference, DOI, URL, licence → English.
2. **Multi-word technical label.** A 2–5 word noun phrase that names a
   component, role, requirement class, or configuration in this document
   → English, the **whole** phrase, one isolate. Covers *X of Y*,
   *Adjective + Name*, and *Name + common noun*.
3. **Inferred lexicon.** Subject lexicon → English at both levels.
   Job lexicon → English at `system-docs`, including the operation verb
   of the same term; at `journal`, Persian unless step 1 or 2 already
   claimed it.
4. **Listed as Persian** in `glossary.md` → Persian.
5. **Otherwise** ordinary scholarly prose → Persian.

Tie-break when steps 1–3 are genuinely uncertain: at `system-docs` keep the
whole noun phrase English; at `journal` write Persian and gloss the English
once, unless the token is clearly part of the subject (`nginx`, `location`).
Record the choice in `terms.tsv` when that file exists. Never resolve
uncertainty by half-translating. Never write the choice into the skill's
glossary.

## The field-term test

A token is a field term of art of one of the named **jobs** when at least
one of these holds:

- it appears in the source document's own glossary or terminology section;
- it appears in the upstream project's official glossary, man page,
  `--help` output, or spec index;
- the source itself marks it as defined — monospace, italics on first
  use, or capitalised mid-sentence.

## Isolation and morphology

Mechanics live in `rtl-bidi.md`. Three rules belong here because they are
terminology decisions, not layout:

- One isolate per whole noun phrase, never one isolate per word.
- Regular English plurals of a kept term drop `-s` / `-es` / `-ies`. The
  singular stem stays in the isolate; Persian `ها` (or `های` / `هایی`)
  follows it: `\en{service}ها`, `\en{platform}ها`, `\en{API}ها`,
  `\en{OpenStack service}ها`. Never `services`, `platforms`, `APIs`,
  `nodes`. Names that merely end in *s* (`Kubernetes`, `Windows`) stay
  as written. Do not attach any other Persian affix (`\en{Go}ی`).
- No Persian head noun in front of an English name. `\en{OpenStack
  service}ها` stays whole; «سرویس‌های OpenStack» is a half-translation,
  not a compromise.

## First mention and consistency

At `system-docs`, no gloss on first mention. At `journal`, one gloss is
allowed the first time a Persian **preferred** term carries an English
concept (and only when that Persian form is the chosen `output`).

One **preferred** form per `concept` for the whole document, in both
directions: never mix `location` and مکان, never mix a preferred English
form with an unisolated bare copy, and never silently upgrade an
`admitted` synonym into a second preferred. For anything longer than a
few pages, produce the concept-oriented `terms.tsv` in
`long-documents.md` **before** translating the body. Pass it with
`--terms terms.tsv` so a calque or deprecated form in chapter nine fails
the build.

## Forbidden output

The canonical house list is `term-pairs.tsv`, not prose. Each row pairs a
source term with the Persian calque that must never replace it, and a
`levels` column: `system-docs` for one-word field nouns (skipped at
`--level journal`) or `all` for multi-word labels kept English at both
levels. The checker reads the whole file. Add a row there in the same
commit as any new Keep-English note in `glossary.md`, then confirm with:

```bash
scripts/check-fa.py path/to/doc.tex --level system-docs --terms terms.tsv --manifest manifest.txt --strict
```

House `system-docs` rows today: `node`, `deployment`, `configuration`,
`implementation`, `integration`, `firewall`, `encryption`, `command`,
`server`, `partition`, `filter`. At `journal` those one-word forms are
Persian unless they are in the inferred subject lexicon. A kept-term
plural is `\en{node}ها`, not `nodes` and not گره‌ها.

`--terms FILE` reads this job's `terms.tsv` and forbids `forbidden_fa`
plus any `deprecated` forms on keep-English rows. An empty
`forbidden_fa` on those rows is an error. Optional columns (`concept`,
`status`, `admitted`, `deprecated`) are ignored when absent so older
five-column files still lint. `--pairs FILE` merges extra rows in
term-pairs format. Neither is a reason to write a glossary file into the
skill.
