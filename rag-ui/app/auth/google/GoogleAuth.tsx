"use client";

import { Button } from "@/components/ui/button";
import { getSupabaseBrowserClient } from "@/lib/supabase/browser-client";
import { toast } from "sonner";

export default function GoogleAuth() {
  const supabase = getSupabaseBrowserClient();

  async function handleGoogleLogin() {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/auth/callback?next=/chat`,
      },
    });

    if (error) {
      toast.error("Không thể đăng nhập với Google.");
    }
  }

  return (
    <Button
      type="button"
      className="h-12 w-full rounded-xl border border-white/10 bg-white text-slate-950 hover:bg-slate-100"
      onClick={handleGoogleLogin}
    >
      <span className="mr-2 inline-flex size-5 items-center justify-center">
        <svg viewBox="0 0 48 48" aria-hidden="true" className="size-5">
          <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.9 29.3 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.9 1.2 8.1 3.1l5.7-5.7C34.1 6.2 29.4 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.2-.4-3.5z" />
          <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 15.4 19 12 24 12c3.1 0 5.9 1.2 8.1 3.1l5.7-5.7C34.1 6.2 29.4 4 24 4c-7.8 0-14.7 4.4-17.7 10.7z" />
          <path fill="#4CAF50" d="M24 44c5.3 0 10-2 13.6-5.3l-6.3-5.2C29 35.3 26.7 36 24 36c-5.3 0-9.7-3.1-11.3-7.5l-6.5 5C9.1 39.8 16 44 24 44z" />
          <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-1.2 3.4-3.9 5.9-7.3 7.1l.1.1 6.3 5.2C33.9 39.1 40 34 40 24c0-1.3-.1-2.2-.4-3.5z" />
        </svg>
      </span>
      Continue with Google
    </Button>
  );
}