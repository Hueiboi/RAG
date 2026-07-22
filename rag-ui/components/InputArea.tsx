"use client";

import { useState } from "react";
import { SendHorizontal, Paperclip, FileText, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface InputAreaProps {
  onSend: (message: string) => void;
  onFileUpload: (file: File) => void;
  onFileRemove: () => void;
  loading: boolean;
  file: File | null;
}

export function InputArea({ onSend, onFileUpload, onFileRemove, loading, file }: InputAreaProps) {
  const [input, setInput] = useState("");

  const handleSubmit = () => {
    if (!input.trim() || loading) return;
    onSend(input);
    setInput("");
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileUpload(e.target.files[0]);
      e.target.value = "";
    }
  };

  return (
    <div className="flex flex-col gap-2">
      {/* File badge */}
      {file && (
        <div className="flex items-center justify-between bg-bg-elevated border border-bg-border rounded-lg px-3 py-1.5 text-xs text-text-secondary">
          <div className="flex items-center gap-2 truncate max-w-[90%]">
            <FileText className="w-4 h-4 text-accent-primary shrink-0" />
            <span className="truncate font-medium">{file.name}</span>
            <span className="text-text-muted">
              ({(file.size / 1024).toFixed(1)} KB)
            </span>
          </div>
          <button
            type="button"
            onClick={onFileRemove}
            className="text-text-muted hover:text-text-primary transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Input row */}
      <div className="flex items-center gap-2 bg-bg-elevated border border-bg-border rounded-xl px-3 py-1.5 focus-within:border-accent-primary focus-within:shadow-[0_0_0_2px_#6366F140] transition-all">
        <label className="cursor-pointer text-text-secondary hover:text-text-primary hover:bg-bg-surface rounded-md p-1.5 transition-colors">
          <input
            type="file"
            accept=".pdf,.txt,.docx"
            className="hidden"
            onChange={handleFileChange}
          />
          <Paperclip className="w-5 h-5" />
        </label>

        <Input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={
            file
              ? "Hỏi bất cứ điều gì về tài liệu này..."
              : "Nhập tin nhắn..."
          }
          className="flex-1 border-none bg-transparent shadow-none focus-visible:ring-0 focus-visible:ring-offset-0 px-1 h-auto text-text-primary placeholder:text-text-muted"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit();
            }
          }}
        />

        <Button
          size="icon"
          onClick={handleSubmit}
          disabled={loading || !input.trim()}
          className="shrink-0 bg-accent-primary hover:bg-accent-primary/80 text-white disabled:opacity-40"
        >
          <SendHorizontal className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}
