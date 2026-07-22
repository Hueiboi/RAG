"use client";

import { User } from "@supabase/supabase-js"
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getSupabaseBrowserClient } from "@/lib/supabase/browser-client";
import { AuthPage } from "@/components/auth-page/AuthPage";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";

type EmailPasswordDemoProps = {
  user: User | null;
};

type Mode = "signin" | "signup";

export default function EmailPasswordDemo({ user }: EmailPasswordDemoProps) {
    const [mode, setMode] = useState<Mode>("signup");
    const [email, setEmail] = useState<string>("");
    const [password, setPassword] = useState<string>("");
    const [status, setStatus] = useState<string>("");
    const [currentUser, setCurrentUser] = useState<User | null>(user);
    const supabase = getSupabaseBrowserClient();
    const router = useRouter();

    useEffect(() => {
        const { data: listener } = supabase.auth.onAuthStateChange((event, session) => {
            setCurrentUser(session?.user ?? null);
        });
        
        return () => {
            listener?.subscription.unsubscribe();
        }
    }, [supabase])

    async function handleSignOut() {
        await supabase.auth.signOut();
        setCurrentUser(null);
        setStatus("Signed out successfully.");
        toast.success("Signed out successfully.");
    }

    async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();
        if (mode === "signup") {
            const { error } = await supabase.auth.signUp({ email, password, options:
                {
                    emailRedirectTo: "http://localhost:3000/chat"
                }
             });
            if (error) {
                setStatus("Error occurred while signing up.");
                toast.error("Error occurred while signing up.");
            } else {
                setStatus("Sign up successful.");
                toast.success("Sign up successful. Please check your email for confirmation.");
            }
        } else {
            const { error } = await supabase.auth.signInWithPassword({ email, password });
            if (error) {
                setStatus("Error occurred while signing in.");
                toast.error("Error occurred while signing in.");
            } else {
                setStatus("Sign in successful.");
                toast.success("Sign in successful.");
                router.push("/chat");
            }
        }
    }

    return (
    <AuthPage
      title="Sign in with Email & Password"
      intro="Sign in to start chatting with your documents."
      steps={[
        "Enter your email and password to sign in.",
        "Don't have an account? Switch to signing up.",
        "Forgot your password? Contact an administrator.",
      ]}
    >
      {!currentUser && (
        <>
          <form
            className="relative overflow-hidden rounded-3xl border border-bg-border bg-bg-surface p-8"
            onSubmit={handleSubmit}
          >
            {/* Subtle accent glow */}
            <div
              className="pointer-events-none absolute -left-6 -top-6 -z-10 h-28 w-36 rounded-full bg-accent-glow blur-2xl"
              aria-hidden="true"
            />
            <div
              className="pointer-events-none absolute -bottom-8 right-4 -z-10 h-24 w-32 rounded-full bg-accent-glow blur-2xl"
              aria-hidden="true"
            />

            <div className="mt-2 flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-text-muted">
                  Credentials
                </p>
                <h3 className="text-xl font-semibold text-text-primary">
                  {mode === "signup" ? "Create an account" : "Welcome back"}
                </h3>
              </div>
              <div className="flex rounded-full border border-bg-border bg-bg-elevated p-1 text-xs font-semibold">
                {(["signup", "signin"] as Mode[]).map((option) => (
                  <button
                    key={option}
                    type="button"
                    aria-pressed={mode === option}
                    onClick={() => setMode(option)}
                    className={`rounded-full px-4 py-1 transition ${mode === option
                      ? "bg-accent-primary text-white"
                      : "text-text-secondary hover:text-text-primary"
                      }`}
                  >
                    {option === "signup" ? "Sign up" : "Sign in"}
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-6 space-y-4">
              <label className="block text-sm font-medium text-text-secondary">
                Email
                <Input
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  required
                  className="mt-2 w-full"
                  placeholder="you@email.com"
                />
              </label>
              <label className="block text-sm font-medium text-text-secondary">
                Password
                <Input
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                  minLength={6}
                  className="mt-2 w-full"
                  placeholder="At least 6 characters"
                />
              </label>
            </div>

            <Button
              type="submit"
              className="mt-6 w-full h-11 text-base bg-accent-primary hover:bg-accent-primary/80 text-white"
            >
              {mode === "signup" ? "Create account" : "Sign in"}
            </Button>

            {status && (
              <p className="mt-4 text-sm text-text-secondary" role="status" aria-live="polite">
                {status}
              </p>
            )}
          </form>
        </>
      )}

      <section className="rounded-3xl border border-bg-border bg-bg-surface p-7">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold text-text-primary">Session</h3>
            <p className="mt-1 text-sm text-text-secondary">
              {currentUser
                ? "Hydrated by getSession + onAuthStateChange."
                : "Sign in to hydrate this panel instantly."}
            </p>
          </div>
          <span
            className={`rounded-full px-3 py-1 text-xs font-semibold ${currentUser
              ? "bg-accent-primary/20 text-accent-primary"
              : "bg-bg-elevated text-text-muted"
              }`}
          >
            {currentUser ? "Active" : "Idle"}
          </span>
        </div>
        {currentUser ? (
          <>
            <dl className="mt-5 space-y-3 text-sm text-text-primary">
              <div className="flex items-center justify-between gap-6">
                <dt className="text-text-secondary">User ID</dt>
                <dd className="font-mono text-xs text-text-primary">{currentUser.id}</dd>
              </div>
              <div className="flex items-center justify-between gap-6">
                <dt className="text-text-secondary">Email</dt>
                <dd className="text-text-primary">{currentUser.email}</dd>
              </div>
              <div className="flex items-center justify-between gap-6">
                <dt className="text-text-secondary">Last sign in</dt>
                <dd className="text-text-primary">
                  {currentUser.last_sign_in_at
                    ? new Date(currentUser.last_sign_in_at).toLocaleString()
                    : "—"}
                </dd>
              </div>
            </dl>
            <Button
              variant="outline"
              className="mt-6 w-full"
              onClick={handleSignOut}
            >
              Sign out
            </Button>
          </>
        ) : (
          <div className="mt-6 rounded-2xl border border-dashed border-bg-border bg-bg-elevated p-5 text-sm text-text-muted">
            Session metadata will show up here after a successful sign in.
          </div>
        )}
      </section>
      <Toaster />
    </AuthPage>
  );
}