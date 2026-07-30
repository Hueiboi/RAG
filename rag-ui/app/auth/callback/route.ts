import { NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabase/server-client'; 

// NOTE: This route is used as a callback for OAuth providers. 
//  It exchanges the authorization code for a session and redirects the user accordingly.
export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get('code');
  const next = searchParams.get('next') ?? '/chat';

  if (code) {
    const supabase = await createSupabaseServerClient();
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    
    if (!error) {
      return NextResponse.redirect(`${origin}${next}`);
    }
  }

  return NextResponse.redirect(`${origin}/auth?error=oauth_failed`);
}