import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'
import { getEnvironmentVariable } from '@/lib/supabase/server-client'

export async function proxy(request: NextRequest) {
  const response = NextResponse.next({
    request: {
      headers: request.headers,
    },
  })

  const { supabaseUrl, supabaseAnonKey } = getEnvironmentVariable()
  const supabase = createServerClient(supabaseUrl, supabaseAnonKey, {
    cookies: {
      get(name: string) {
        return request.cookies.get(name)?.value
      },
      set(name: string, value: string, options: CookieOptions) {
        request.cookies.set({ name, value, ...options })
        response.cookies.set({ name, value, ...options })
      },
      remove(name: string, options: CookieOptions) {
        request.cookies.set({ name, value: '', ...options })
        response.cookies.set({ name, value: '', ...options })
      },
    },
  })

  const { data: { user } } = await supabase.auth.getUser()

  if (request.nextUrl.pathname.startsWith('/chat') && !user) {
    return NextResponse.redirect(new URL('/auth/email-password', request.url))
  }

  if (request.nextUrl.pathname.startsWith('/auth') && user) {
    return NextResponse.redirect(new URL('/chat', request.url))
  }

  return response
}

export const config = {
  matcher: ['/chat/:path*', '/auth/:path*'], 
}   