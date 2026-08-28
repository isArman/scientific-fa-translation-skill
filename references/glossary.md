# House glossary

Domain-agnostic lists. The policy that decides which list a token belongs to
lives in `terminology.md`; do not re-derive it here. The forbidden Persian
calques live in `term-pairs.tsv` where the checker can read them.

This file is the only glossary in the skill. There are no per-field packs.
Infer a document's **three jobs** and **subject** from the source
(DevOps, networking, Linux + nginx, not a pack id). Append a row here **only** if it generalises past the
document in hand (chrome, a keep-English class, or a recurring
infrastructure noun). A directive, opcode, or byline from one book does
not belong here — lock it in that job's `terms.tsv` if the document is
long, then discard the file with the job.

## Always Persian

Document chrome. Step 0 of the decision procedure: these are Persian at
every level, and no source glossary overrides them. Applies to the bare
label only — a heading that names an artifact stays English.

| English | Persian |
| --- | --- |
| abstract | چکیده |
| introduction | مقدمه |
| methods / materials and methods | روش‌ها / مواد و روش‌ها |
| results | نتایج |
| discussion | بحث |
| conclusion | نتیجه‌گیری |
| related work | کارهای مرتبط |
| acknowledgments | سپاسگزاری |
| contents / table of contents / brief contents | فهرست مطالب |
| foreword | سخن مقدمه |
| preface | پیشگفتار |
| about this book | دربارهٔ این کتاب |
| about the author | دربارهٔ نویسنده |
| references / bibliography | منابع |
| figure | شکل |
| table | جدول |
| equation | معادله |
| section | بخش |
| appendix | پیوست |
| paper / article | مقاله |
| book | کتاب |
| chapter | فصل |
| copyright | حق نشر |
| changelog | تاریخچه تغییرات |
| credits | سپاسگزاری |

## Persian unless it is this document's field term

Ordinary scholarly vocabulary. Persian by default, English when the
field-term test in `terminology.md` says the source is using it as its own
defined lexicon. This is the tier that used to contradict itself: `dataset`
is مجموعه داده in a clinical paper and `dataset` in an ML paper, and both
are correct.

| English | Persian | Stays English when |
| --- | --- | --- |
| method | روش | part of a named method |
| analysis / study | بررسی | named study or corpus |
| hypothesis | فرضیه | — |
| experiment | آزمایش | — |
| dataset | مجموعه داده | ML lexicon, or a named corpus (`ImageNet`, `GLUE`) |
| specification | مشخصات | the document *is* a spec |
| limitation | محدودیت | — |
| motivation | انگیزه | — |
| rationale | استدلال | — |
| tradeoffs | بده‌بستان‌ها | — |
| alternatives | جایگزین‌ها | — |
| activation | فعال‌سازی | protocol activation (BIP 8/9) |
| invalid | نامعتبر | a defined validity state |
| policy | سیاست | `service policyها` and similar labels |
| spam | هرزنامه | — |
| steganography | پنهان‌نگاری | — |
| grandfathering | معافیت عطف‌به‌ماسبق | — |

## Keep English — classes

Non-exhaustive by design. Anything of the same kind stays English even when
unlisted; that is what makes step 1 of the decision procedure workable.

| Class | Examples |
| --- | --- |
| Algorithms, models, architectures | `transformer`, `backpropagation`, `gradient descent`, `Adam`, `BERT`, `ResNet` |
| Libraries, tools, products, projects | `PyTorch`, `NumPy`, `TensorFlow`, `Kubernetes`, `OpenStack`, `Bitcoin` |
| Protocols and standards | `HTTP`, `AMQP`, `Segwit`, `Taproot` |
| Acronyms | `API`, `PCR`, `GPU`, `CI`, `CPU`, `TPU`, `RMSE`, `BLEU`, `RAM` |
| Statistical symbols | `p`, `n`, `M`, `SD`, `SE`, `df` |
| SI units | `km`, `ms`, `°C`, `GiB` |
| Code and identifiers | anything inside a listing; `scriptPubKey`, `fit(x)` |
| People, journals, conferences | author bylines, venue names, `et al.` |
| Locators | DOI, URL, arXiv id, licence names (`MIT`, `BSD-3-Clause`) |

## Universal terms of art

The recurring infrastructure lexicon. These stay English in any technical
document at `system-docs` level, including the operation verb of the same
term. Each has a row in `term-pairs.tsv` with `levels` `system-docs`, so
the checker fails the build on the Persian calque unless `--level journal`.

| Term | Also covers |
| --- | --- |
| node / nodeها | `controller node`, `compute node`, `Other nodeها` |
| deployment / deploy | `deployment and configuration` |
| configuration / configure | `Install and configure components` |
| implementation / implement | `reference implementation` |
| integration | — |
| firewall / firewallها | `firewalling serviceها`, `restrictive firewallها` |
| encryption | — |
| command / commandها | `command-line clientها` |
| server | `physical server`, `database server` |
| partition | `single disk partition` |
| filter | — |

At `journal` level these become Persian unless the surrounding phrase is a
named artifact or a multi-word label.

## Job terms

Do not create `glossary.local.md`. The working tree holds `terms.tsv`
(`long-documents.md`) so chapter three and chapter nine
use the same form. Keep-English rows for the inferred job and subject
lexicon belong there, with a required `forbidden_fa` calque for the checker.
That file is discarded with the job. Never copy it into this skill.

```bash
scripts/check-fa.py doc.tex --level system-docs --terms terms.tsv --manifest manifest.txt --strict
```
