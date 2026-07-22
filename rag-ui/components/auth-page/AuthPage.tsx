"use client";

import type { ReactNode } from "react";

type AuthPageProps = {
  title: string;
  intro: string;
  children: ReactNode;
};

export function AuthPage({
  title,
  intro,
  children,
}: AuthPageProps) {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,rgba(30,41,59,0.95)_0%,rgba(15,23,42,1)_45%,rgba(2,6,23,1)_100%)] text-slate-100">
      <main className="mx-auto flex min-h-screen w-full max-w-md items-center px-5 py-10 sm:px-6">
        <div className="w-full rounded-[2rem] border border-white/10 bg-slate-900/90 p-6 shadow-[0_30px_80px_rgba(0,0,0,0.45)] backdrop-blur-xl sm:p-8">
          <div className="text-center">
            <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
              RAG Auth
            </p>
            <h1 className="mt-2 text-2xl font-semibold text-slate-50">
              {title}
            </h1>
            <p className="mt-3 text-sm leading-6 text-slate-400">
              {intro}
            </p>
          </div>

          <div className="mt-6">{children}</div>
        </div>
      </main>
    </div>
  );
}

