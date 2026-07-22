import EmailPassword from "@/app/auth/email-password/EmailPassword";
import { createSupabaseServerClient } from "@/lib/supabase/server-client";


export default async function EmailPasswordPage() {
    const supabase = await createSupabaseServerClient();
    const {
        data: { user },
    } = await supabase.auth.getUser();

    return (
        <div className="h-screen flex flex-col">
            <div className="flex-1 overflow-y-auto">
                <EmailPassword user={user} />
            </div>
        </div>   
    );
}