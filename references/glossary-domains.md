# Domain packs

Field-specific vocabulary, kept out of `glossary.md` so the house list stays
short and so a term from one field cannot leak into another. Read only the
pack that matches the source. Pack names match the `scope` column of
`term-pairs.tsv`:

```bash
scripts/check-fa.py doc.tex --level system-docs --domains openstack --strict
```

Everything below is Keep English unless a row says otherwise. Rows are the
whole **source** phrase. In the translation, a regular English plural of a
kept term is the singular stem plus `ها` (`\en{OpenStack service}ها`, not
`OpenStack services`); see `terminology.md`.

## openstack

Cloud install guides and service documentation.

| Term | Also covers |
| --- | --- |
| OpenStack services | `OpenStack packages`, `OpenStack architecture`, `OpenStack components` |
| Identity service | `Image service`, `Compute service`, `Networking service`, `Block Storage node` |
| controller node | `compute node`, `additional nodeها`, `Other nodeها` |
| provider networks | `provider network`, `self-service networks` |
| AMQP message broker | `message broker`, `message queue` |
| web-based user interface | `browser plug-ins`, `command-line clients` |
| database | `database password`, `database passwords`, `database server` |
| password security | `password`, `passwords`, `service account passwords`, `user name/password` |
| interrelated services | `supporting services`, `complementary services`, `advanced services` |
| example architecture | `functional example architecture`, `minimum configuration` |
| Hardware requirements | `hardware requirements`, `minimum requirements`, `system requirements`, `hardware resources` |
| performance and redundancy requirements | — |
| Ubuntu Cloud archive repository | `RDO repository` |
| account with administrative privileges | — |
| underlying infrastructure | — |
| Network layout | figure caption, kept whole |
| Default ports that OpenStack components use | table caption, kept whole |
| Default ports that secondary services related to OpenStack components use | table caption, kept whole |
| Get started with OpenStack | heading |
| Conceptual architecture | `Logical architecture`, `The OpenStack architecture` |
| Host networking | heading |
| Install and configure components | heading |

`password` is this pack's most error-prone row: it reads like ordinary prose
and drifts to گذرواژه in glossaries and screenshots even when the body keeps
it English. Enforced by the `openstack` scope in `term-pairs.tsv`.

## bitcoin

Protocol specifications, BIPs, script and consensus documents.

| Term | Also covers |
| --- | --- |
| transaction / block / miner | field nouns; never تراکنش / بلوک / استخراج‌کننده in this lexicon |
| fee | never کارمزد in this lexicon |
| consensus | `soft fork`, `hard fork` |
| activation | `deployment` parameters, BIP 8/9 activation states |
| Taproot, Tapleaf, Tapscript, Taptree | output and script family |
| Segwit, BitVM, Miniscript | protocol, product, language names |
| inscription, pay-to-contract, blobspace | named schemes |
| GetBlockTemplate, GBT | protocol / API names |
| scriptPubKey, scriptSig, redeemScript | identifiers |
| witness, annex, control block, keypath | named stack and spend artifacts |
| UTXO, P2WPKH, P2WSH, P2TR, P2A, BIP, NUMS | acronyms |
| OP_RETURN, OP_PUSHDATA, OP_SUCCESS, OP_IF, OP_NOTIF | opcodes; joined pairs are one isolate |
| LOCKED_IN, ACTIVE, DEFINED, STARTED, EXPIRED, FAILED | BIP 9 states |
| BIP9, BIP8, BIP16, BIP141, BIP341, BIP342, BIP433, BIP-3 | identifiers |

State transitions and opcode pairs arrive joined by punctuation
(`STARTED -> LOCKED_IN`, `OP_IF/OP_NOTIF`) and must be a single isolate.

## kubernetes

| Term | Also covers |
| --- | --- |
| Kubernetes cluster | `Kubernetes clusters`; never «خوشه Kubernetes» |
| namespace, controller, operator, sidecar | field nouns |
| Custom Resource Definition, CRD | — |
| control plane | `worker node` |

## gitops

Flux, Argo, and continuous-delivery documentation.

| Term | Also covers |
| --- | --- |
| GitOps Toolkit | — |
| composable APIs | never «APIهای ترکیب‌پذیر»; output is `\en{composable API}ها` |
| reusable Go packages | never «بسته‌های Go»; output is `\en{reusable Go package}ها` |
| Continuous Delivery workflows | — |
| version-controlled approach to operations | keep whole; do not calque |
| reconciliation, drift, source controller | field nouns |

## observability

Prometheus, Grafana, OpenTelemetry, and monitoring runbooks. Not a
generic DevOps pack: `metric` is a field noun here and ordinary prose
in a statistics paper.

| Term | Also covers |
| --- | --- |
| metric, trace, span | never سنجه / ردیابی / دهانه in this lexicon |
| exporter | Prometheus / OpenTelemetry exporter |
| scrape target | `scrape`, `scrape interval` |
| service level objective | `SLO`; never هدف سطح خدمت |
| service level indicator | `SLI`; never شاخص سطح خدمت |
| cardinality | label cardinality in a time-series store; never کثرت برچسب |
| dashboard | Grafana / Prometheus dashboard; never تابلوی کنترل |

`metric` is this pack's most error-prone row: it reads like ordinary
prose and drifts to سنجه. Enforced by the `observability` scope in
`term-pairs.tsv`. Lint with `--domains observability`.

## containers

Docker, containerd, and OCI runtime documentation. Kubernetes cluster
vocabulary stays in the `kubernetes` pack; Helm chart/release/values
belong there too.

| Term | Also covers |
| --- | --- |
| container | never ظرف in this lexicon |
| container image | never تصویر ظرف or تصویر کانتینر; not a bare «تصویر» |
| image registry | `registry`; never انباره تصویر |
| overlay filesystem | `overlayfs` |
| container runtime | `runtime`; never زمان اجرای ظرف |

`container` is this pack's most error-prone row. Enforced by the
`containers` scope in `term-pairs.tsv`. Lint with `--domains containers`.

## ci

GitHub Actions, GitLab CI, Jenkins — build and test, not delivery.
The `gitops` pack covers Flux/Argo CD.

| Term | Also covers |
| --- | --- |
| pipeline | never خط لوله in this lexicon |
| runner | `GitHub-hosted runner`, `self-hosted runner` |
| artifact | `build artifact`; never مصنوع |
| workflow | GitHub Actions / GitLab CI workflow, not a GitOps reconciliation loop |

`pipeline` is this pack's most error-prone row. Enforced by the `ci`
scope in `term-pairs.tsv`. Lint with `--domains ci`. Do not pass
`--domains gitops` instead of this pack.

## iac

Terraform, OpenTofu, Pulumi, and Ansible. `state` as ordinary
«وضعیت» is not a row — only the labeled IaC phrases.

| Term | Also covers |
| --- | --- |
| playbook | Ansible playbook; never کتابچه اجرا |
| inventory | Ansible inventory; never سیاهه موجودی |
| module | Terraform / Pulumi module; never پیمانه |
| provider | Terraform provider; never ارائه‌دهنده |
| state file | Terraform state file; never فایل وضعیت |
| remote state | Terraform remote state; never وضعیت راه‌دور |

`playbook` and `state file` are the error-prone rows. Enforced by the
`iac` scope in `term-pairs.tsv`. Lint with `--domains iac`.

## linux

systemd, journald, and cgroup documentation. `unit` and `journal` as
ordinary Persian واحد / ژورنال are not rows — only the labeled phrases.

| Term | Also covers |
| --- | --- |
| cgroup | never گروه کنترل in this lexicon |
| systemd unit | never واحد سیستم‌دی |
| systemd journal | `journald`; never ژورنال سیستم‌دی |

`cgroup` is this pack's most error-prone row. Enforced by the `linux`
scope in `term-pairs.tsv`. Lint with `--domains linux`.

## ml

Machine-learning papers. Usually read at `journal` level, where one-word
field nouns become Persian — so this pack is mostly named artifacts.

| Term | Also covers |
| --- | --- |
| transformer, backpropagation, gradient descent | architectures and methods |
| Adam, AdamW, SGD | optimiser names |
| BERT, GPT, ResNet, YOLO | model names |
| PyTorch, NumPy, TensorFlow, JAX | libraries |
| ImageNet, GLUE, COCO | named corpora; a *named* dataset is a product |
| RMSE, BLEU, F1, AUC | metrics |

`dataset` as a common noun is مجموعه داده at `journal` level; as a named
corpus it is English. That split is the reason this pack exists rather than
a universal `dataset` rule. Lint ML papers with
`--level journal --domains ml`.

## Adding a pack

1. New file section here, named after the scope you will pass to
   `--domains`.
2. Rows for the whole source phrases, not single words, unless the single
   word passes the field-term test.
3. For every term that a translator would plausibly calque, add a row to
   `term-pairs.tsv` with that scope. A pack without checker rows is
   documentation, not enforcement.
