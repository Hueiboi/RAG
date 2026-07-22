"use client";

import { User } from '@supabase/supabase-js'
import { LogOut } from "lucide-react"
import { getSupabaseBrowserClient } from "@/lib/supabase/browser-client"
import { useRouter } from "next/navigation"
import { toast } from "sonner"
  
export default function UserBadge({ user }: { user: User | null }) {
    const supabase = getSupabaseBrowserClient()
    const router = useRouter()

    if (!user) return null

    async function handleSignOut() {
        await supabase.auth.signOut()
        toast.success("Signed out successfully.")
        router.push("/auth")
    }

    return (
        <div className="flex items-center gap-2.5">
            {/* Avatar: initials, accent-primary bg, 32px, rounded-full */}
            <div className="w-8 h-8 rounded-full bg-accent-primary flex items-center justify-center text-white text-xs font-bold shrink-0">
                {user.email?.charAt(0).toUpperCase() || "?"}
            </div>
            {/* Email: text-secondary, text-sm */}
            <span className="text-text-secondary text-sm max-w-36 truncate">
                {user.email}
            </span>
            {/* Sign Out: ghost, text-secondary, hover:text-error */}
            <button
                onClick={handleSignOut}
                className="inline-flex items-center justify-center rounded-md h-8 w-8 text-text-secondary hover:text-status-error hover:bg-bg-elevated transition-colors"
                title="Sign out"
            >
                <LogOut className="w-4 h-4" />
            </button>
        </div>
    )
}