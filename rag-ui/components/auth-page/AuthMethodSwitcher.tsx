"use client";

import { User } from "@supabase/supabase-js";
import EmailPassword from "@/app/auth/email-password/EmailPassword";
import GoogleAuth from "@/app/auth/google/GoogleAuth";
import { Toaster } from "@/components/ui/sonner";

type AuthMethodSwitcherProps = {
  user: User | null;
};

export default function AuthMethodSwitcher({ user }: AuthMethodSwitcherProps) {
  return (
    <div>
        <div className="space-y-5 text-slate-100">
            <EmailPassword user={user} />

            <div className="flex items-center gap-3 py-1 text-[0.7rem] uppercase tracking-[0.24em] text-slate-500">
            <span className="h-px flex-1 bg-white/10" />
            <span>or continue with</span>
            <span className="h-px flex-1 bg-white/10" />
            </div>
            <GoogleAuth />
        </div>

      <Toaster />
    </div>
      
  );
}