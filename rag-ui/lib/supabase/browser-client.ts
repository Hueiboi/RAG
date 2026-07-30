"use client";
import { createBrowserClient} from "@supabase/ssr";
import type { SupabaseClient } from "@supabase/supabase-js";

type SupabaseSchema = Record<string, never>; 

let client: SupabaseClient<SupabaseSchema> | null = null;


// NOTE: This function is used to create a Supabase client for the browser.
// It uses the environment variables NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY to initialize the client. 
// If the client has already been created, it returns the existing client instance.
export function getSupabaseBrowserClient(): SupabaseClient<SupabaseSchema> {
    if(client) {
        return client;
    }

    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if(!supabaseUrl || !supabaseAnonKey) {
        throw new Error("Missing Supabase environment variables. Please check your .env.local file.");
    }

    client = createBrowserClient<SupabaseSchema>(supabaseUrl, supabaseAnonKey);
    return client;
}