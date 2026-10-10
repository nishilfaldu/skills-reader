export const siteUrl = 'https://skills-reader.vercel.app';
export const siteName = 'skills reader';
export const siteDescription = 'A reading guide for Matt Pocock\'s agent skills, plus the explanations and skill source from the repository.';
export const shareImage = '/opengraph-image.png';

export function docsUrl(slug?: string[]) {
  return `${siteUrl}/docs${slug?.length ? `/${slug.join('/')}` : ''}`;
}
