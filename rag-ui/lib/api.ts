import { ApiResponse, ChatResponse, UploadResponse } from '@/lib/types'

// NOTE: This API wrapper is used to send requests to the FastAPI backend.
// It handles errors and returns a consistent response format.
export const chatApi = {
  sendMessage: async (question: string): ApiResponse<ChatResponse> => {
    try {
      const res = await fetch(`${process.env.FAST_API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
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

  uploadFile: async (file: File): ApiResponse<UploadResponse> => {
    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${process.env.FAST_API_URL}/upload`, {
        method: "POST",
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
  }
};