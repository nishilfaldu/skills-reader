# skills reader

An unofficial reading site for [Matt Pocock's skills](https://github.com/mattpocock/skills), built with Next.js and Fumadocs. The guide is the linear reading path. The explanations are the `docs/` pages from that repository. The source library is every `SKILL.md` and the notes beside it.

Install commands in the guide are copied from the canonical block in `.agents/install-block.md`.

## Local development

```bash
npm install
npm run dev
```

Open http://localhost:3000. `npm run check:content` checks routes, source coverage, and sidebar entries. `npm run build` checks the production build.

## Refresh from upstream

The current content was copied from `mattpocock/skills` commit `49dd158d1076134a641b33efb035946536778336`. Clone that commit to `/tmp/mattpocock-skills`, then run:

```bash
python3 scripts/sync-content.py
npm run check:content
npm run build
```

Copied material keeps its upstream MIT license in `UPSTREAM-LICENSE`. The guide chapters in `content/docs/0*.mdx` are not overwritten by the sync.

## Deployment

This repository deploys to Vercel as `skills-reader`. The canonical URL is [skills-reader.vercel.app](https://skills-reader.vercel.app). Favicon, Apple touch icon, and the social preview can be regenerated with `npm run generate:brand`.
