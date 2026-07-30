"use client";

import { User } from "@supabase/supabase-js"
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getSupabaseBrowserClient } from "@/lib/supabase/browser-client";
import { toast } from "sonner";

type EmailPasswordProps = {
  user: User | null;
};

type Mode = "signin" | "signup";

export default function EmailPasswordDemo({ user }: EmailPasswordProps) {
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

    async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();
        if (mode === "signup") {
            const { error } = await supabase.auth.signUp({ email, password, options:
                {
                    emailRedirectTo: `${process.env.NEXT_PUBLIC_API_URL}/chat`
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
    <form
      className="space-y-4"
      onSubmit={handleSubmit}
    >
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Email login</p>
          <h3 className="mt-1 text-lg font-semibold text-slate-50">
            {mode === "signup" ? "Create your account" : "Sign in to continue"}
          </h3>
        </div>
        <div className="rounded-full border border-white/10 bg-white/5 p-1 text-xs font-medium text-slate-300">
          {mode === "signup" ? "Sign up" : "Sign in"}
        </div>
      </div>

      <div className="flex rounded-full border border-white/10 bg-white/5 p-1 text-xs font-semibold">
        {(["signin", "signup"] as Mode[]).map((option) => (
          <button
            key={option}
            type="button"
            aria-pressed={mode === option}
            onClick={() => setMode(option)}
            className={`h-10 flex-1 rounded-full px-4 transition ${mode === option
              ? "bg-white text-slate-950"
              : "text-slate-300 hover:text-white"
              }`}
          >
            {option === "signin" ? "Sign In" : "Sign Up"}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        <label className="block text-sm text-slate-300">
          <Input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
            className="mt-2 h-12 w-full rounded-xl border-white/10 bg-white/5 px-3 text-slate-100 placeholder:text-slate-500"
            placeholder="Enter your email"
          />
        </label>
        <label className="block text-sm text-slate-300">
          <Input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
            minLength={6}
            className="mt-2 h-12 w-full rounded-xl border-white/10 bg-white/5 px-3 text-slate-100 placeholder:text-slate-500"
            placeholder="Enter your password"
          />
        </label>
      </div>

      <Button
        type="submit"
        className="h-12 w-full rounded-xl bg-white text-slate-950 hover:bg-slate-100"
      >
        {mode === "signup" ? "Sign Up" : "Sign In"}
      </Button>

      {status && (
        <p className="text-sm text-slate-400" role="status" aria-live="polite">
          {status}
        </p>
      )}
    </form>
  );
}