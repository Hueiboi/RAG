import { createSupabaseServerClient } from "@/lib/supabase/server-client"
import { NextResponse, type NextRequest } from 'next/server'


// NOTE: Middleware này được sử dụng để kiểm tra trạng thái xác thực của người dùng trước khi truy cập các route /chat và /auth.
// Nếu người dùng chưa đăng nhập và cố gắng truy cập /chat, họ sẽ được chuyển hướng đến /auth.
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