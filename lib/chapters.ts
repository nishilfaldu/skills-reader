export const chapters = [
  { slug: '', title: 'The skills guide' },
  { slug: '01-install', title: 'Install the skills' },
  { slug: '02-setup', title: 'Run setup once per repo' },
  { slug: '03-align', title: 'Grill the plan before anyone writes code' },
  { slug: '04-language', title: 'Build a shared language' },
  { slug: '05-spec', title: 'Turn the conversation into a spec and tickets' },
  { slug: '06-wayfinder', title: 'Plan work that does not fit one session' },
  { slug: '07-build', title: 'Implement with a feedback loop' },
  { slug: '08-design', title: 'Keep the modules deep' },
  { slug: '09-ship', title: 'Review, open the PR, then retro' },
  { slug: '10-shelf', title: 'Triage, research, and the rest of the shelf' },
] as const;

export const chapterHref = (slug: string) => slug ? `/docs/${slug}` : '/docs';
