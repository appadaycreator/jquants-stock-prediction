"use client";

import { X } from "lucide-react";
import React from "react";

interface SideDetailPanelProps {
  open: boolean;
  title?: string;
  onClose?: () => void;
  children?: React.ReactNode;
}

export default function SideDetailPanel({ open, title = "詳細", onClose, children }: SideDetailPanelProps) {
  return (
    <div className={`fixed inset-y-0 right-0 z-40 w-full max-w-md transform transition-transform duration-300 ${open ? "translate-x-0" : "translate-x-full"}`}>
      <div className="h-full bg-white border-l border-gray-200 shadow-xl flex flex-col">
        <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <h3 className="text-base font-semibold text-gray-900">{title}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600" aria-label="close">
            <X className="h-5 w-5" />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          {children}
        </div>
      </div>
    </div>
  );
}


