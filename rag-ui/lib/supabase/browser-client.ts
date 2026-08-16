"use client";
import { createBrowserClient} from "@supabase/ssr";
import type { SupabaseClient } from "@supabase/supabase-js";

type SupabaseSchema = Record<string, never>; 

let client: SupabaseClient<SupabaseSchema> | null = null;


// NOTE: Hàm này được sử dụng để tạo và trả về một Supabase client cho trình duyệt. 
// Nếu client đã tồn tại, nó sẽ trả về client hiện tại.
// Nếu chưa tồn tại, nó sẽ tạo một client mới bằng cách sử dụng URL và khóa ẩn của Supabase từ biến môi trường. 
// Nếu các biến môi trường này không được thiết lập, nó sẽ ném ra một lỗi.
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