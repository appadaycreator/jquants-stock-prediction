"use client";

import { Todo } from "@/types/today";
import { useState } from "react";

interface TodoCardProps {
  todo: Todo;
  index: number;
}

export default function TodoCard({ todo, index }: TodoCardProps) {
  const [isCompleted, setIsCompleted] = useState(false);

  const getTodoIcon = (type: string) => {
    switch (type) {
      case "order":
        return "📋";
      case "review":
        return "🔍";
      case "monitor":
        return "👀";
      default:
        return "📝";
    }
  };

  const getTodoColor = (type: string) => {
    switch (type) {
      case "order":
        return "bg-blue-50 border-blue-200 text-blue-800";
      case "review":
        return "bg-yellow-50 border-yellow-200 text-yellow-800";
      case "monitor":
        return "bg-green-50 border-green-200 text-green-800";
      default:
        return "bg-gray-50 border-gray-200 text-gray-800";
    }
  };

  const handleToggle = () => {
    setIsCompleted(!isCompleted);
    // ここで実際の完了状態を保存
    console.log(`Todo ${index} ${!isCompleted ? "completed" : "uncompleted"}`);
  };

  return (
    <div className={`rounded-lg border p-4 transition-all ${
      isCompleted ? "opacity-60 bg-gray-50" : getTodoColor(todo.type)
    }`}>
      <div className="flex items-start gap-3">
        <div className="text-2xl">
          {getTodoIcon(todo.type)}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-semibold">
              {todo.title}
            </h4>
            <span className="text-sm font-medium">
              ({todo.count}件)
            </span>
          </div>
          <div className="flex items-center gap-2 mt-2">
            <button
              onClick={handleToggle}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                isCompleted
                  ? "bg-green-100 text-green-700 hover:bg-green-200"
                  : "bg-white text-gray-700 hover:bg-gray-50 border border-gray-300"
              }`}
            >
              {isCompleted ? "✓ 完了" : "未完了"}
            </button>
            {isCompleted && (
              <span className="text-sm text-green-600 font-medium">
                完了済み
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
