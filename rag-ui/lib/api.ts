import { ApiResponse, ChatResponse, DocumentsResponse, UploadResponse, ChatHistory } from '@/lib/types'
import { createBrowserClient } from '@supabase/ssr'

const supabase = createBrowserClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

const base_url = process.env.NEXT_PUBLIC_FAST_API_URL;

// getAuthHeader là một hàm bất đồng bộ (async function) => trả về Promise. 
// Sau cùng nó sẽ trả về một đối tượng K/V: Record<string, string>.
async function getAuthHeader(): Promise<Record<string, string>> {
  const { data: { session } } = await supabase.auth.getSession();
  return session ? { Authorization: `Bearer ${session.access_token}` } : {};
}

// NOTE: API wrapper này cung cấp các phương thức để gửi tin nhắn và tải lên tệp tin đến server.
// Giúp việc giao tiếp với server trở nên dễ dàng hơn và quản lý lỗi một cách hiệu quả.
// getAuthHeader được sử dụng để lấy thông tin xác thực từ Supabase và thêm vào header của các yêu cầu API.
export const chatApi = {
  sendMessage: async (question: string): ApiResponse<ChatResponse> => {
    try {
      const authHeader = await getAuthHeader();
      const res = await fetch(`${base_url}/chat`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json", 
          ...authHeader },
        body: JSON.stringify({ question })
      });

      const result = await res.json();

      if (!res.ok) {
        return { data: null, error: result.detail || "Gửi tin nhắn thất bại" };
      }

      return { data: result, error: null };
    } catch (err: unknown) {
      return { data: null, error: (err as Error).message || "Không thể kết nối đến Server" };
    }
  },

  getDocuments: async (): ApiResponse<DocumentsResponse> => {
    try {
      const authHeader = await getAuthHeader();
      const res = await fetch(`${base_url}/documents`, {
        method: "GET",
        headers: { ...authHeader }
      });

      const result = await res.json();

      if (!res.ok) {
        return { data: null, error: result.detail || "Lấy danh sách tài liệu thất bại" };
      }

      return { data: result, error: null };
    } catch (err: unknown) {
      return { data: null, error: (err as Error).message || "Không thể kết nối đến Server" };
    }
  },

  deleteDocument: async (fileName: string): ApiResponse<{ message: string }> => {
    try {
      const authHeader = await getAuthHeader();
      const res = await fetch(`${base_url}/documents/${encodeURIComponent(fileName)}`, {
        method: "DELETE",
        headers: { ...authHeader }
      });

      const result = await res.json();

      if (!res.ok) {
        return { data: null, error: result.detail || "Xóa tài liệu thất bại" };
      }

      return { data: result, error: null };
    } catch (err: unknown) {
      return { data: null, error: (err as Error).message || "Không thể kết nối đến Server" };
    }
  },

  uploadFile: async (file: File): ApiResponse<UploadResponse> => {
    try {
      const authHeader = await getAuthHeader();
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${base_url}/upload`, {
        method: "POST",
        headers: { ...authHeader },
        body: formData
      });

      const result = await res.json();

      if (!res.ok) {
        return { data: null, error: result.detail || "Upload file thất bại" };
      }

      return { data: result, error: null };
    } catch (err: unknown) {
      return { data: null, error: (err as Error).message || "Không thể kết nối đến Server" };
    }
  },
  saveMessage: async (message: {role: string, content: string}): ApiResponse<void> => {
    try {
      const authHeader = await getAuthHeader();
      const res = await fetch(`${base_url}/history`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...authHeader
        },
        body: JSON.stringify(message)
      });

      const result = await res.json();

      if (!res.ok) {
        return { data: null, error: result.detail || "Lưu lịch sử thất bại" };
      }

      return { data: result, error: null };
    } catch (err: unknown) {
      return { data: null, error: (err as Error).message || "Không thể kết nối đến Server" };
    }
  },
  getHistory: async (): ApiResponse<{history: ChatHistory[]}> => {
    try {
      const authHeader = await getAuthHeader();
      const res = await fetch(`${base_url}/history`, {
        headers: {
          "Content-Type": "application/json",
          ...authHeader
        }
      })

      const result = await res.json()

      if(!res.ok) return { data: null, error: result.detail || "Đồng bộ lịch sử thất bại" };

      return {data: result, error: null}
    } catch (err: unknown) {
      return { data: null, error: (err as Error).message || "Không thể kết nối đến Server" };
    }
  }
};