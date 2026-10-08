# Frontend README - Next.js + Supabase Auth

![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=nextdotjs&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![Supabase](https://img.shields.io/badge/Supabase-Auth%20%26%20Session-3ECF8E?logo=supabase&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)

> Frontend của hệ thống RAG: đăng nhập bằng Supabase, vào chat, upload tài liệu và gửi câu hỏi sang backend.

## Tổng Quan Giao Diện

Frontend được xây theo App Router của Next.js và chia thành các luồng chính:

| Route | Vai trò |
| --- | --- |
| `/login` | Luồng đăng nhập. Hiện tại được triển khai bằng `/auth/email-password` |
| `/chat` | Màn hình chat chính và upload document |

Ngoài ra, `proxy.ts` chặn route để bảo vệ trải nghiệm:

- Chưa đăng nhập thì vào `/chat` sẽ bị redirect về trang auth.
- Đã đăng nhập thì vào nhóm route auth sẽ được redirect sang `/chat`.

## Các Luồng Trang

### Auth flow

- `app/auth/email-password/page.tsx` lấy session từ server client.
- `app/auth/email-password/EmailPassword.tsx` xử lý signup/signin/signout.
- `supabase.auth.signUp()` đang cấu hình redirect email về `/chat`.

### Chat flow

- `app/chat/page.tsx` load session, hiển thị gate login nếu chưa có user.
- Khi có user, màn hình chat cho phép gửi câu hỏi và chọn file để upload.
- `lib/api.ts` gọi backend FastAPI ở `http://localhost:8000/api`.

## Cấu Hình Frontend

Frontend dùng `.env.local` trong `rag-ui/`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

### Lưu ý

- Hai biến này được đọc bởi cả browser client và server client trong `lib/supabase`.
- Nếu thiếu biến, app sẽ throw lỗi rõ ràng ngay khi tạo Supabase client.

## Chạy Frontend

```bash
cd rag-ui
npm install
npm run dev
```

Mặc định app chạy ở `http://localhost:3000`.

## Nhật Ký Phát Triển & Lỗi Đã Gặp

### 1) Sự cố Git nested submodule với folder `rag-ui`

**Triệu chứng:** `rag-ui` bị Git nhận nhầm là nested repo hoặc submodule, khiến commit/push và status trở nên rối.

**Cách khắc phục:**

1. Kiểm tra xem bên trong `rag-ui` có thư mục `.git` riêng không.
2. Nếu có, xóa `.git` nội bộ để folder này trở về thư mục bình thường.
3. Thêm lại `rag-ui/` như một phần của repo chính.

**Bài học:** nếu frontend chỉ là một app con trong monorepo, đừng để nó tự mang Git history riêng trừ khi bạn thật sự muốn dùng submodule.

### 2) Tích hợp Supabase Auth (Email/Password & Google OAuth)

**Email/Password:**

- `EmailPassword.tsx` hỗ trợ signup và signin.
- Khi signup, app gửi email confirmation và redirect về `/chat` sau khi xác thực.

**Google OAuth:**

- Dự án đã dành sẵn khu vực auth flow cho provider khác.
- Nếu bật Google OAuth, chỉ cần cấu hình provider trong Supabase và dùng cùng session/client pattern hiện tại.

**Bài học:** tách riêng browser client và server client giúp auth session hoạt động ổn định hơn giữa client-side navigation và server-side rendering.

## Troubleshooting

| Vấn đề | Nguyên nhân | Cách xử lý |
| --- | --- | --- |
| Đăng nhập xong vẫn bị redirect | Session chưa hydrate kịp | Kiểm tra `proxy.ts` và `onAuthStateChange` |
| Chat không gọi được backend | Backend chưa chạy hoặc sai URL | Chạy FastAPI và kiểm tra `lib/api.ts` |
| API chưa chặt chẽ | Thiếu Type/Interface | Thêm `ApiResponse<T> = Promise<{ data:T , error: string}>`
| Google OAuth không sút sang /chat (bị reload lại /auth) | Thiếu Route Handler để đổi OAuth Code lấy Session Cookie | Tạo app/auth/callback/route.ts dùng exchangeCodeForSession và trỏ redirectTo về đó |
| Google OAuth báo lỗi Redirect URL | Chưa đăng ký URL callback trên Supabase Dashboard | Thêm http://localhost:3000/auth/callback vào mục Redirect URLs trên Supabase |
| Lấy data.answer bị lỗi Type / undefined | Backend FastAPI trả về { answer } khi thành công nhưng trả về { detail } khi có lỗi	| Kiểm tra if (!res.ok) để lấy result.detail cho error, ngược lại mới trả result cho data |

## File Quan Trọng

| File | Vai trò |
| --- | --- |
| `app/chat` | UI chat chính |
| `app/auth/` | Đăng nhập / đăng ký |
| `lib/api.ts` | Client gọi backend |
| `lib/supabase/browser-client.ts` | Supabase client cho browser |
| `lib/supabase/server-client.ts` | Supabase client cho server |
| `proxy.ts` | Route guard cho auth |

## Note 
- **Mount/Unmount component**
    ```typescript
    // Mount   = component được tạo ra và hiển thị lên DOM
    // Unmount = component bị xóa khỏi DOM (navigate sang trang khác, logout...)

    useEffect(() => {
    // Code ở đây chạy khi MOUNT

    return () => {
        // Code ở đây chạy khi UNMOUNT ← cleanup function
    };
    }, []); // Điều kiện useEffect load
    ```
- **Race condition**: Thêm cancelled flag
    Timeline **!w/** cancelled flag:
        t=0: user login → getHistory() bắt đầu fetch
        t=1: user logout → setMessages([]) → reset
        t=2: fetch xong → setMessages(data) ← GHI ĐÈ LÊN! bug

    Timeline **w/** cancelled flag:
        t=0: user login → getHistory() bắt đầu fetch
        t=1: user logout → currentUser = null
            → useEffect cleanup chạy → cancelled = true
        t=2: fetch xong → if (cancelled) return ← bỏ qua, không ghi đè

- **Call api miss edge case**
    > Khi vào case error nhớ reset state và dùng toast/message alert (VD: setHistoryLoading(false) -> tránh loading vô tận dù bị lỗi)
