// API Response wrapper
export type ApiResponse<T> = Promise<{ data: T | null; error: string | null }>

// Chat
export interface ChatResponse {
    answer: string
}

// Upload
export interface UploadResponse {
    message: string
    filename: string
}

// Message UI
export interface Message {
    id: string
    role: "user" | "assistant"
    content: string
}
