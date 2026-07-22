"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Bot, LogIn } from "lucide-react";
import { toast } from "sonner";
import { Toaster } from "@/components/ui/sonner";
import { chatApi } from "@/lib/api";
import { MessageBubble } from "@/components/MessageBubble";
import { InputArea } from "@/components/InputArea";
import UserBadge from "@/components/UserBadge";
import { getSupabaseBrowserClient } from "@/lib/supabase/browser-client";
import type { User as SupabaseUser } from "@supabase/supabase-js";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [file, setFile] = useState<File | null>(null);
  const [currentUser, setCurrentUser] = useState<SupabaseUser | null>(null);
  const [authReady, setAuthReady] = useState(false);

  const supabase = getSupabaseBrowserClient();
  const router = useRouter();
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      setCurrentUser(user);
      setAuthReady(true);
    });

    const { data: listener } = supabase.auth.onAuthStateChange((_event, session) => {
      setCurrentUser(session?.user ?? null);
    });

    return () => {
      listener?.subscription.unsubscribe();
    };
  }, [supabase]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (message: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: message,
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      if (file) {
        toast.info("Đang xử lý tài liệu...");
        await chatApi.uploadFile(file);
        toast.success("Nạp tài liệu thành công!");
        setFile(null);
      }

      const data = await chatApi.sendMessage(message);

      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: data.answer,
        },
      ]);
    } catch (error) {
      console.error("Lỗi hệ thống RAG:", error);
      toast.error("Có lỗi xảy ra, vui lòng thử lại.");
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (uploadedFile: File) => {
    setFile(uploadedFile);
  };

  // -- Auth gate --
  if (authReady && !currentUser) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-bg-base p-4">
        <div className="w-full max-w-sm">
          <div className="flex flex-col items-center text-center">
            <div className="w-16 h-16 rounded-full bg-bg-surface border border-bg-border flex items-center justify-center mb-6">
              <Bot className="w-8 h-8 text-accent-primary" />
            </div>
            <h1 className="text-xl font-semibold text-text-primary mb-2">
              RAG Knowledge Base
            </h1>
            <p className="text-sm text-text-secondary mb-8 max-w-xs">
              Đăng nhập để truy vấn tài liệu thông minh với AI.
            </p>
            <Button
              className="w-full h-12 text-base gap-2 bg-accent-primary hover:bg-accent-primary/80 text-white"
              onClick={() => router.push("/auth")}
            >
              <LogIn className="w-5 h-5" />
              Đăng nhập
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // -- Chat --
  return (
    <div className="flex flex-col h-screen bg-bg-base">
      {/* Header */}
      <header className="border-b border-bg-border px-4 lg:px-6 py-3 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2.5">
          <Bot className="w-6 h-6 text-accent-primary" />
          <h1 className="text-lg font-semibold text-text-primary">RAG Assistant</h1>
        </div>
        <div className="flex items-center gap-3">
          {!currentUser ? (
            <Button
              variant="outline"
              size="sm"
              className="gap-1.5 text-xs"
              onClick={() => router.push("/auth")}
            >
              <LogIn className="w-3.5 h-3.5" />
              Đăng nhập
            </Button>
          ) : (
            <UserBadge user={currentUser} />
          )}
        </div>
      </header>

      {/* Messages */}
      <ScrollArea className="flex-1 px-4 lg:px-6 py-4">
        <div className="max-w-2xl mx-auto space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-[50vh] text-center space-y-3">
              <Bot className="w-12 h-12 text-text-muted stroke-[1.5]" />
              <p className="text-sm font-medium text-text-secondary">
                Chưa có cuộc hội thoại nào.
              </p>
              <p className="text-xs text-text-muted max-w-xs">
                Hãy tải lên một tài liệu (PDF, Docx, TXT) và đặt câu hỏi để AI truy vấn thông tin.
              </p>
            </div>
          )}

          {messages.map((msg, idx) => {
            const isLatestBot =
              msg.role === "assistant" && idx === messages.length - 1;
            return (
              <MessageBubble
                key={msg.id}
                role={msg.role}
                content={msg.content}
                isLatestBot={isLatestBot}
              />
            );
          })}

          {loading && (
            <div className="flex gap-3 justify-start">
              <div className="w-8 h-8 rounded-full bg-bg-surface border border-bg-border flex items-center justify-center animate-pulse">
                <Bot className="w-4 h-4 text-text-muted" />
              </div>
              <div className="bg-bg-surface border border-bg-border text-text-secondary rounded-[18px_18px_18px_4px] px-4 py-2.5 text-sm animate-pulse">
                Đang truy vấn tài liệu và suy nghĩ...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Input area */}
      <div className="border-t border-bg-border px-4 lg:px-6 py-3 shrink-0">
        <div className="max-w-2xl mx-auto">
          <InputArea
            onSend={handleSend}
            onFileUpload={handleFileUpload}
            onFileRemove={() => setFile(null)}
            loading={loading}
            file={file}
          />
        </div>
      </div>
      <Toaster />
    </div>
  );
}