"use client";

import React from "react";
import { ExternalLink, Globe, BookOpen, Info } from "lucide-react";

interface ExternalLinkItem {
  name: string;
  url: string;
  type?: "wikipedia" | "official" | "documentation" | "other";
}

interface ExternalLinksProps {
  links: ExternalLinkItem[];
  className?: string;
}

export default function ExternalLinks({ links, className = "" }: ExternalLinksProps) {
  if (!links || links.length === 0) {
    return null;
  }

  const getIcon = (type?: string) => {
    switch (type) {
      case "wikipedia":
        return <BookOpen size={14} className="text-blue-600" />;
      case "official":
        return <Globe size={14} className="text-green-600" />;
      case "documentation":
        return <Info size={14} className="text-purple-600" />;
      default:
        return <ExternalLink size={14} className="text-gray-600" />;
    }
  };

  const getTypeLabel = (type?: string) => {
    switch (type) {
      case "wikipedia":
        return "Wikipedia";
      case "official":
        return "公式";
      case "documentation":
        return "ドキュメント";
      default:
        return "外部リンク";
    }
  };

  return (
    <div className={`space-y-2 ${className}`}>
      <h4 className="text-sm font-medium text-gray-900 flex items-center gap-2">
        <Globe size={16} className="text-gray-600" />
        外部リンク
      </h4>
      
      <div className="space-y-2">
        {links.map((link, index) => (
          <a
            key={index}
            href={link.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors group"
          >
            <div className="flex-shrink-0">
              {getIcon(link.type)}
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="font-medium text-gray-900 group-hover:text-blue-600 transition-colors">
                {link.name}
              </div>
              <div className="text-xs text-gray-500">
                {getTypeLabel(link.type)}
              </div>
            </div>
            
            <ExternalLink size={12} className="text-gray-400 group-hover:text-blue-600 transition-colors" />
          </a>
        ))}
      </div>
      
      <div className="text-xs text-gray-500 mt-2">
        ※ 外部リンクは新しいタブで開きます
      </div>
    </div>
  );
}
