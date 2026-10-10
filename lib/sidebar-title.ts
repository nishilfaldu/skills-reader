const names: Record<string, string> = {
  adr: 'ADR', api: 'API', cli: 'CLI', github: 'GitHub', gitlab: 'GitLab',
  html: 'HTML', json: 'JSON', matt: 'Matt', mdx: 'MDX', openai: 'OpenAI',
  pocock: 'Pocock', pr: 'PR', tdd: 'TDD', ui: 'UI', url: 'URL', yaml: 'YAML',
};

export function sidebarTitle(title: string, url?: string): string {
  if (url === '/docs/about') return 'About';
  let first = true;
  return title.replace(/[A-Za-z][A-Za-z0-9]*/g, (word) => {
    const known = names[word.toLowerCase()];
    const alreadyStyled = word !== word.toLowerCase() && word !== word.toUpperCase();
    const acronym = word === word.toUpperCase() && word.length > 1;
    const replacement = known ?? (alreadyStyled || acronym
      ? word
      : first
        ? word[0].toUpperCase() + word.slice(1).toLowerCase()
        : word.toLowerCase());
    first = false;
    return replacement;
  });
}
