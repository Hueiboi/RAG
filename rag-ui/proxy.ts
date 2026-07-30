import { createSupabaseServerClient } from "@/lib/supabase/server-client"
import { NextResponse, type NextRequest } from 'next/server'


// NOTE: This middleware is used to protect the /chat route and redirect to /auth if the user is not authenticated.
//  It also redirects to /chat if the user is authenticated and tries to access /auth.
export async function proxy(request: NextRequest) {
  const response = NextResponse.next({
    request: {
      headers: request.headers,
    },
  })

  const supabase = await createSupabaseServerClient()

  const { data: { user } } = await supabase.auth.getUser()

  if (request.nextUrl.pathname.startsWith('/chat') && !user) {
    return NextResponse.redirect(new URL('/auth', request.url))
  }

  if (request.nextUrl.pathname.startsWith('/auth') && user) {
    return NextResponse.redirect(new URL('/chat', request.url))
  }

  return response
}

export const config = {
  matcher: ['/chat/:path*', '/auth/:path*'], 
}   