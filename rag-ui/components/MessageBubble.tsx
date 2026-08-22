"use client";

import { Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";
import Markdown from "react-markdown";
import remarkGfm from 'remark-gfm'


interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
  isLatestBot?: boolean;
}

export function MessageBubble({ role, content, isLatestBot }: MessageBubbleProps) {
  const isUser = role === "user";

  return (
    <div className={cn("flex gap-3", isUser ? "justify-end" : "justify-start")}>
      {/* Bot avatar */}
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-bg-surface flex items-center justify-center shrink-0 border border-bg-border">
          <Bot className="w-4 h-4 text-text-secondary" />
        </div>
      )}

      {/* Bubble */}
      <div
        className={cn(
          "px-4 py-2.5 text-[15px] leading-relaxed",
          isUser
            ? "bg-accent-primary text-white rounded-[18px_18px_4px_18px] max-w-[70%]"
            : "bg-bg-surface border border-bg-border text-text-primary rounded-[18px_18px_18px_4px] max-w-[80%] [&_code]:font-mono [&_pre]:font-mono",
          !isUser && isLatestBot && "animate-glow-fade"
        )}
      >
        <Markdown remarkPlugins={[remarkGfm]}>{content}</Markdown>
      </div>

      {/* User avatar */}
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-accent-primary flex items-center justify-center shrink-0 text-white">
          <User className="w-4 h-4" />
        </div>
      )}
    </div>
  );
}
