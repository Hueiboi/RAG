"use client";

import { useCallback, useEffect, useState } from "react";
import { File, FileText, Loader2, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { chatApi } from "@/lib/api";
import type { DocumentItem } from "@/lib/types";
import ConfirmDialog from "@/components/ConfirmDialog";

interface SidebarProps {
  refreshKey: number;
}

export function formatFileSize(size: number | null | undefined): string {
  if (size == null) return "—";
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(2)} MB`;
}

export function formatUploadDate(date: string | null | undefined): string {
  if (!date) return "—";
  const d = new Date(date);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleDateString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

function fileIcon(name: string) {
  const ext = name.split(".").pop()?.toLowerCase();
  if (ext === "pdf" || ext === "docx") {
    return <FileText className="w-4 h-4 text-accent-primary shrink-0" />;
  }
  return <File className="w-4 h-4 text-text-secondary shrink-0" />;
}

export default function Sidebar({ refreshKey }: SidebarProps) {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [confirmTarget, setConfirmTarget] = useState<DocumentItem | null>(null);

  const applyResult = ({ data, error }: Awaited<ReturnType<typeof chatApi.getDocuments>>) => {
    if (error || !data) {
      setError(error || "Không thể tải danh sách tài liệu.");
      setDocuments([]);
    } else {
      setError(null);
      setDocuments(data.documents);
    }
    setLoading(false);
  };

  const loadDocuments = useCallback(async () => {
    await chatApi.getDocuments().then(applyResult);
  }, []);

  useEffect(() => {
    chatApi.getDocuments().then(applyResult);
  }, [refreshKey]);

  const handleRetry = () => {
    setLoading(true);
    setError(null);
    loadDocuments();
  };

  const handleConfirmDelete = async () => {
    const target = confirmTarget;
    setConfirmTarget(null);
    if (!target) return;

    setDeleting(target.name);
    const { error } = await chatApi.deleteDocument(target.name);
    setDeleting(null);

    if (error) {
      toast.error(`Xóa file thất bại: ${error}`);
      return;
    }

    toast.success("Đã xóa tài liệu.");
    setLoading(true);
    loadDocuments();
  };

  return (
    <aside className="w-65 shrink-0 h-full flex flex-col bg-bg-surface border-l border-bg-border">
      <div className="px-4 py-3 border-b border-bg-border shrink-0">
        <h2 className="text-sm font-semibold text-text-primary">
          Tài liệu đã upload
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-4 space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="flex items-start gap-2.5">
                <div className="w-4 h-4 rounded-sm bg-bg-elevated animate-pulse" />
                <div className="flex-1 space-y-1.5">
                  <div className="h-3.5 w-3/4 rounded bg-bg-elevated animate-pulse" />
                  <div className="h-2.5 w-1/2 rounded bg-bg-elevated animate-pulse" />
                </div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="p-4">
            <p className="text-xs text-text-secondary">{error}</p>
            <button
              onClick={handleRetry}
              className="mt-2 text-xs text-accent-primary hover:underline"
            >
              Thử lại
            </button>
          </div>
        ) : documents.length === 0 ? (
          <div className="flex items-center justify-center h-40 px-4 text-center">
            <p className="text-xs text-text-muted leading-relaxed">
              Chưa có tài liệu nào. Upload file để bắt đầu.
            </p>
          </div>
        ) : (
          <ul>
            {documents.map((doc) => (
              <li
                key={doc.name}
                title={doc.name}
                className="group flex items-start gap-2.5 px-4 py-2.5 hover:bg-bg-elevated transition-colors"
              >
                {fileIcon(doc.name)}
                <div className="flex-1 min-w-0">
                  <p className="text-[13px] text-text-primary truncate leading-snug">
                    {doc.name}
                  </p>
                  <p className="text-[11px] text-text-secondary mt-0.5">
                    {formatFileSize(doc.size)} · {formatUploadDate(doc.created_at)}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setConfirmTarget(doc)}
                  disabled={deleting !== null}
                  aria-label={`Xóa ${doc.name}`}
                  className="shrink-0 mt-0.5 p-1 rounded-md text-text-muted hover:text-status-error hover:bg-bg-base transition-colors disabled:opacity-40"
                >
                  {deleting === doc.name ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Trash2 className="w-3.5 h-3.5" />
                  )}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <ConfirmDialog
        isOpen={confirmTarget !== null}
        fileName={confirmTarget?.name ?? ""}
        onConfirm={handleConfirmDelete}
        onCancel={() => setConfirmTarget(null)}
      />
    </aside>
  );
}
