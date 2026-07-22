"use client";

import type { ReactNode } from "react";

type AuthPageProps = {
  title: string;
  intro: string;
  steps: string[];
  children: ReactNode;
};

export function AuthPage({
  title,
  intro,
  steps,
  children,
}: AuthPageProps) {
  return (
    <div className="flex min-h-screen flex-col bg-bg-base text-text-primary">
      <header className="border-b border-bg-border bg-bg-surface/60 backdrop-blur-md">
        <div className="mx-auto flex w-full max-w-5xl items-center justify-between px-6 py-5">
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-text-muted">
              RAG Auth
            </p>
            <h1 className="text-2xl font-semibold text-text-primary">{title}</h1>
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-5xl px-6 py-12">
        <div className="grid gap-8 lg:grid-cols-[0.95fr_1.05fr]">
          <section className="rounded-3xl border border-bg-border bg-bg-surface p-8">
            <p className="text-lg font-medium text-text-primary">{intro}</p>
            <ol className="mt-5 list-decimal space-y-2 pl-5 text-sm text-text-secondary">
              {steps.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ol>
          </section>
          <div className="flex flex-col gap-6">{children}</div>
        </div>
      </main>
    </div>
  );
}