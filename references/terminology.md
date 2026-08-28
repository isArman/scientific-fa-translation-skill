# Terminology policy

Single owner of the keep-English / write-Persian split.
`scientific-style.md` owns register and orthography, `glossary.md` holds
the house lists (document chrome, keep-English classes, recurring
infrastructure nouns), and `term-pairs.tsv` is the machine-readable half
that `scripts/check-fa.py` enforces. Do not restate this policy anywhere
else.

There is no per-field glossary in this skill. Infer the **jobs** and the
**subject** from the source in hand. Do not look up a pack name, and do
not write terms into `glossary.md`.

## Level

Two levels, because a sysadmin install guide and a journal paper cannot take
the same treatment. Announce the level in the first chat message.

| Level | For | Job lexicon (one-word field nouns) |
| --- | --- | --- |
| `system-docs` (default) | books, install guides, protocol specs, product docs, RFC/BIP, runbooks | English (`deployment`, `upstream`, `configure`) |
| `journal` | papers, theses, review articles for a general scientific audience | Persian, unless the token is in the subject lexicon |

The **subject** lexicon (product, protocol, tool the document is about) stays
English at both levels. The level only moves the boundary for the **job**
lexicon — ordinary one-word terms of the practice — and their operation
verbs. The user switches with «سطح journal» or «سطح system-docs».

## Infer job and subject

Before classifying tokens, read enough of the source to name these, and
announce them with the level:

- **Jobs** — exactly **three** short practice labels, ranked by how much
  of the source they cover (`DevOps`, `networking`, `Linux`). A book
  often spans more than one profession; three is both the target and the
  cap. Each label must be a real thread in the source (a chapter,
  audience, or repeated terms of art). Do not invent a practice the
  source does not use, and do not add a fourth. The **job lexicon** is
  the union of those three.
- **Subject** — one product, protocol, or corpus (`nginx`, Bitcoin,
  ImageNet, …)

Those names are not pack ids and are not looked up in this repository.
Example: jobs DevOps, networking, Linux; subject nginx; level
`system-docs`.

Then every term that belongs to that job lexicon **or** that subject's
lexicon stays English: directives, modules, CLI flags, config keys,
named blocks, operation verbs of those terms, and multi-word labels in
that lexicon.

A token belongs to the inferred lexicon when at least one of these holds:

- it is a name, directive, module, flag, API, or config key of the subject
  (`nginx`, `location`, `proxy_pass`, `worker_processes`);
- it is a term of art of one of the three jobs as this document uses it
  (the field-term test below);
- it appears in the source's own glossary, or in that subject's man page,
  `--help`, or spec index.

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

A token is a field term of art of one of the three **jobs** when at least
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
allowed the first time a Persian term carries an English concept.

One form per concept for the whole document, in both directions: never mix
`location` and مکان, and never mix `location` with an unisolated bare
`location`. For anything longer than a few pages, produce the `terms.tsv`
described in `long-documents.md` **before** translating the body. That
file is job memory, not a skill glossary. Pass it to the checker with
`--terms terms.tsv` so a calque in chapter nine fails the build.

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

`--terms FILE` reads this job's `terms.tsv` and forbids the required
calque column on keep-English rows. An empty `forbidden_fa` on those
rows is an error. `--pairs FILE` merges extra rows in
term-pairs format. Neither is a reason to write a glossary file into the
skill.
