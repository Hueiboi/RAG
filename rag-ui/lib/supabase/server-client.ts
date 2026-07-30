import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

export function getEnvironmentVariable(): { supabaseUrl: string; supabaseAnonKey: string } {
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if(!supabaseUrl || !supabaseAnonKey) {
        throw new Error("Missing Supabase environment variables. Please check your .env.local file.");
    }

    return { supabaseUrl, supabaseAnonKey };
}

// NOTE: This function is used to create a Supabase client for the server.
// It uses the environment variables NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY to initialize the client. 
// It also uses the cookies from the request to maintain the session.
export async function createSupabaseServerClient() {
    const { supabaseUrl, supabaseAnonKey } = getEnvironmentVariable();
    const cookieStore = await cookies();

    return createServerClient(supabaseUrl, supabaseAnonKey, { 
        cookies: {
            getAll() {
                return cookieStore.getAll();
            },
            setAll(cookiesToSet) {
                try {
                    cookiesToSet.forEach(({ name, value, options }) => 
                    cookieStore.set(name, value, options));
                }
                catch (error) {
                    console.error("Error setting cookies:", error);
                }
            }
        }
     });
}