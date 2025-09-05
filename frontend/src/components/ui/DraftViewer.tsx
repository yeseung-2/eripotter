"use client";

export default function DraftViewer({ html }: { html: string }) {
  if (!html) return null;
  const looksLikeHtml = /<[^>]+>/.test(html);
  return looksLikeHtml ? (
    <div className="prose max-w-none bg-white border rounded p-4" dangerouslySetInnerHTML={{ __html: html }} />
  ) : (
    <pre className="bg-white border rounded p-4 whitespace-pre-wrap">{html}</pre>
  );
}
