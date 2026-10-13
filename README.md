# EIC Knowledge Guide

Explanatory documentation for the ePIC software stack, generated from the source code:
how reconstruction works detector by detector, which algorithms run, what the
configuration flags do, and where the numbers come from. Published at
https://eic.github.io/knowledge-guide.

The pages are drafts written by an AI assistant from [eic/EICrecon](https://github.com/eic/EICrecon)
and [eic/epic](https://github.com/eic/epic) at a stated commit. Every claim links to the
file it came from; verify there before depending on it.

## Provenance and review

Every page under `docs/` carries, in its front matter:

```yaml
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft          # or reviewed, with reviewed_by and reviewed
```

`tools/check_provenance.py` runs on every pull request and refuses a page without these
fields. A page becomes `reviewed` through a pull request from someone who checked it
against the source, adding `reviewed_by: <GitHub login>` and `reviewed: <date>`.

Every Monday `tools/stale_pages.py` compares each page's cited source files with the
repository's default branch and keeps the issue "pages behind their source" up to date.
A page listed there is regenerated or corrected, with `source_commit` and `generated`
moved to the new commit.

## Indexing after a publish

The Pages workflow, after deploying, tells the search indexers to re-read this
repository, so a merged page is searchable within minutes rather than at the next
scheduled refresh. Each call runs only when its repository variable is set:

| variable | secret | calls |
| --- | --- | --- |
| `EIC_DOCS_MCP_URL` | `EIC_DOCS_REFRESH_TOKEN` | `POST <url>/refresh` on a hosted eic-docs-mcp |
| `EIC_SEARCH_URL` | `EIC_SEARCH_ADMIN_TOKEN` | `POST <url>/ingest/run` for source `eic_knowledge_guide` on the EIC smart-search service |

## Contributing

Corrections through pull requests, even small ones: a wrong number or a dead link is a
one-line change. A new page needs the front matter above and a link to its source for
every claim. Reviews route through `CODEOWNERS`.

Preview locally:

```bash
bundle install && bundle exec jekyll serve
```

## Used by

- [eic-docs-mcp](https://github.com/eic/eic-docs-mcp), the documentation search for AI
  assistants, indexes this repository:
  ```yaml
  - name: knowledge-guide
    url: https://github.com/eic/knowledge-guide
    branch: main
    pages: https://eic.github.io/knowledge-guide
    files: [index.md, "docs/**/*.md"]
  ```
- The search box on [eic.github.io](https://eic.github.io), through the EIC smart-search
  service.
