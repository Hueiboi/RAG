import { redirect } from "next/navigation"

// Root chỉ làm cổng vào app. Việc kiểm tra đã đăng nhập thuộc về proxy.ts:
// chưa đăng nhập sẽ bị đá tiếp từ /chat sang /auth.
export default function Home() {
  redirect("/chat")
}
