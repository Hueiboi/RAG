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

// Documents list
export interface DocumentItem {
    name: string
    size: number | null
    created_at: string | null
}

export interface DocumentsResponse {
    documents: DocumentItem[]
}

// Message UI
export interface Message {
    id: string
    role: "user" | "assistant"
    content: string
}
