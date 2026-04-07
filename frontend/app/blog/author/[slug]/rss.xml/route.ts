import { getAuthorBySlug } from '@/lib/authors';
import { getArticlesByAuthor } from '@/lib/blog';

/**
 * S11: Per-author RSS feed.
 * Route: GET /blog/author/[slug]/rss.xml
 */
export async function GET(
  _request: Request,
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params;
  const author = getAuthorBySlug(slug);
  if (!author) {
    return new Response('Not Found', { status: 404 });
  }

  const baseUrl = process.env.NEXT_PUBLIC_CANONICAL_URL || 'https://smartlic.tech';
  const articles = getArticlesByAuthor(slug);

  const items = articles
    .sort((a: { publishDate: string }, b: { publishDate: string }) => new Date(b.publishDate).getTime() - new Date(a.publishDate).getTime())
    .map((article: { title: string; slug: string; description: string; publishDate: string; category: string }) => {
      const pubDate = new Date(article.publishDate + 'T12:00:00-03:00');
      return `    <item>
      <title><![CDATA[${article.title}]]></title>
      <link>${baseUrl}/blog/${article.slug}</link>
      <description><![CDATA[${article.description}]]></description>
      <pubDate>${pubDate.toUTCString()}</pubDate>
      <guid isPermaLink="true">${baseUrl}/blog/${article.slug}</guid>
      <category><![CDATA[${article.category}]]></category>
      <author>${author.name}</author>
    </item>`;
    })
    .join('\n');

  const rss = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>${author.name} — SmartLic Blog</title>
    <link>${baseUrl}/blog/author/${slug}</link>
    <description>Artigos de ${author.name} sobre licitações públicas, inteligência artificial e mercado B2G.</description>
    <language>pt-BR</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    <atom:link href="${baseUrl}/blog/author/${slug}/rss.xml" rel="self" type="application/rss+xml" />
${items}
  </channel>
</rss>`;

  return new Response(rss, {
    headers: {
      'Content-Type': 'application/rss+xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600, s-maxage=3600',
    },
  });
}
