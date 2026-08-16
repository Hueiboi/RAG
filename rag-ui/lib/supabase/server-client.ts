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

// NOTE: Hàm createSupabaseServerClient được sử dụng để tạo một client Supabase trên server-side
// Sử dụng cookie từ request hiện tại để quản lý phiên người dùng.
// Nó trả về một client Supabase được cấu hình với URL và khóa ẩn từ biến môi trường.
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