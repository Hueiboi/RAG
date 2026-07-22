import { createSupabaseServerClient } from "@/lib/supabase/server-client";
import { AuthPage } from "@/components/auth-page/AuthPage";
import AuthMethodSwitcher from "@/components/auth-page/AuthMethodSwitcher";

export default async function AuthLandingPage() {
  const supabase = await createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  return (
    <AuthPage
      title="Sign in"
      intro="Choose Google or email/password on the same page."
    >
      <AuthMethodSwitcher user={user} />
    </AuthPage>
  );
}