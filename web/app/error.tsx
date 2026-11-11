"use client";

export default function ErrorPage({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return <main className="state-page"><h1>Executive overview</h1><p>The validated aggregate contract could not be loaded.</p><button type="button" onClick={reset}>Retry</button></main>;
}
