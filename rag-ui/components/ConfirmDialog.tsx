"use client";

import {
  Dialog,
  DialogContent,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Trash2, FileText } from "lucide-react";

interface ConfirmDialogProps {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  fileName: string;
}

export default function ConfirmDialog({
  isOpen,
  onConfirm,
  onCancel,
  fileName,
}: ConfirmDialogProps) {
  return (
    <Dialog
      open={isOpen}
      onOpenChange={(open) => {
        if (!open) onCancel();
      }}
    >
      <DialogContent
        showCloseButton={false}
        className="border border-[#2A2A38] bg-[#111118] p-6 shadow-xl sm:max-w-100"
      >
        {/* Header */}
        <div className="flex items-center gap-3 mb-2">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-red-500/10">
            <Trash2 className="h-4 w-4 text-red-500" />
          </div>
          <p className="text-[15px] font-medium text-[#F0F0FF]">
            Xác nhận xóa tài liệu
          </p>
        </div>

        {/* Body */}
        <div className="ml-12 space-y-3">
          <p className="text-[13px] leading-relaxed text-[#8888AA]">
            Bạn sắp xóa
          </p>

          {/* File badge */}
          <div className="flex items-center gap-2 rounded-md border border-red-500/20 bg-red-500/8 px-3 py-2">
            <FileText className="h-3.5 w-3.5 shrink-0 text-red-400" />
            <span className="break-all text-[13px] font-medium text-[#F0F0FF]">
              {fileName}
            </span>
          </div>

          <p className="text-[13px] leading-relaxed text-[#8888AA]">
            Hành động này sẽ xóa file và toàn bộ dữ liệu liên quan. Không thể
            hoàn tác.
          </p>
        </div>

        <DialogFooter className="mt-2 gap-2">
          <Button
            variant="ghost"
            onClick={onCancel}
            className="border border-[#2A2A38] text-[#8888AA] hover:bg-[#1A1A24] hover:text-[#F0F0FF]"
          >
            Hủy
          </Button>
          <Button
            onClick={onConfirm}
            className="gap-1.5 bg-red-500 text-white hover:bg-red-600"
          >
            <Trash2 className="h-3.5 w-3.5" />
            Xóa tài liệu
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}