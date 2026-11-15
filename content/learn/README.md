# content/learn

Plain-language /learn articles (WS3 content lane). One folder per article, one Markdown file per language:

```
content/learn/<slug>/<lang>.md     e.g. content/learn/winter-range/nl.md
content/learn/index.yaml           order and titles per language
```

Languages: `en`, `nl`, `de`, `fr`, `es`, `it`. EN and NL are written first; a missing language falls back to EN.

## Front matter

Every file starts with YAML front matter:

| Field | Required | Meaning |
|---|---|---|
| `title` | yes | Page title in this language. Must match `index.yaml`. |
| `slug` | yes | Folder name; the same in every language. |
| `lang` | yes | `en`, `nl`, `de`, `fr`, `es` or `it`. |
| `review` | yes | `needed` (draft, not yet checked by a person) or `done`. |
| `updated` | yes | Date of the last content change, `YYYY-MM-DD`. |
| `glossary` | yes | Every term id used inline in the body (see below). Only ids that exist in `data/taxonomy/glossary_terms.yaml`, `chemistries.yaml` or `voltage_classes.yaml`. |
| `sources` | yes | List of `{title, url, retrieved}` for every source the text links to. `retrieved` is the date the source was last checked. |

Translations share the same `glossary` and `sources` lists as the EN file unless the text differs.

## Glossary terms inline

Mark a glossary term in the body with double square brackets, so the renderer can attach an ⓘ tooltip:

- `[[term-id|shown text]]`: shows *shown text* (in the page's language) with the tooltip of `term-id`. Use this form by default, so the sentence reads naturally.
- `[[term-id]]`: shows the term's own label from the glossary, in the page's language.

`term-id` is a glossary id (`heat-pump`), a chemistry id (`lfp`) or a voltage-class id (`800v`). Chemistry and voltage-class ids link to the `chemistry` and `voltage-class` learn pages, like the existing `/learn/[term]` route does for `related` ids. An unknown id renders as plain text with no ⓘ (never a crash), and the check below should catch it first.

## Writing rules

- B1 level: short sentences, short paragraphs, plain words; explain a technical term the first time or mark it as a glossary term.
- Every factual claim links to its rule or statistic, inline as a normal Markdown link, and the source is listed in `sources`. If a figure can't be sourced, say it qualitatively ("often", "many cars") or leave it out. Never invent numbers.
- Metric units and euros. Give the date ("as of 1 July 2026") with every statistic.
- Maker claims are labelled as claims. Things that change often (two-way charging offers) say so.
- No brand name of our own in the text; use "we" / "our".

## Check

Quick consistency check (front matter parses, inline ids are listed in `glossary` and exist in the taxonomy):

```
python3 -I - <<'EOF'
import yaml, re, glob
ids = set()
for f, k in [("glossary_terms", "glossary_terms"), ("chemistries", "chemistries"), ("voltage_classes", "voltage_classes")]:
    ids |= {r["id"] for r in yaml.safe_load(open(f"data/taxonomy/{f}.yaml"))[k]}
for p in sorted(glob.glob("content/learn/*/*.md")):
    _, fm, body = open(p).read().split("---\n", 2)
    m = yaml.safe_load(fm)
    inline = set(re.findall(r"\[\[([a-z0-9-]+)(?:\|[^\]]*)?\]\]", body))
    bad = (inline | set(m["glossary"])) - ids
    print(p, "OK" if not bad and inline == set(m["glossary"]) else f"CHECK {bad or inline ^ set(m['glossary'])}")
EOF
```
