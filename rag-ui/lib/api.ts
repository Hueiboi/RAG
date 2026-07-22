const BASE_URL = "http://localhost:8000/api"

export const chatApi = {
  sendMessage: async (question: string) => {
    const res = await fetch(`${BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    })
    return res.json()
  },

  uploadFile: async (file: File) => {
    const formData = new FormData()
    formData.append("file", file)
    const res = await fetch(`${BASE_URL}/upload`, {
      method: "POST",
      body: formData
    })
    return res.json()
  }
}