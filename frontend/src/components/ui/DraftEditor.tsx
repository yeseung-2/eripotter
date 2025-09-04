"use client";

import { useState, useEffect } from "react";

interface DraftEditorProps {
  initialContent: string;
  onSave: (content: string) => void;
  onCancel: () => void;
  loading?: boolean;
}

export default function DraftEditor({ 
  initialContent, 
  onSave, 
  onCancel, 
  loading = false 
}: DraftEditorProps) {
  const [content, setContent] = useState(initialContent);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    setContent(initialContent);
  }, [initialContent]);

  const handleSave = () => {
    onSave(content);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setContent(initialContent);
    setIsEditing(false);
  };

  if (!isEditing) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-md font-medium text-gray-700">생성된 초안</h3>
          <button
            onClick={() => setIsEditing(true)}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            편집
          </button>
        </div>
        <div className="border rounded-lg p-4 bg-gray-50 max-h-96 overflow-y-auto">
          <div 
            className="prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{ __html: content }}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-md font-medium text-gray-700">초안 편집</h3>
        <div className="flex gap-2">
          <button
            onClick={handleCancel}
            disabled={loading}
            className="px-3 py-1 text-sm border border-gray-300 text-gray-700 rounded hover:bg-gray-50 disabled:opacity-50"
          >
            취소
          </button>
          <button
            onClick={handleSave}
            disabled={loading}
            className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
          >
            {loading ? "저장 중..." : "저장"}
          </button>
        </div>
      </div>
      <div className="border rounded-lg">
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full h-96 p-4 border-0 resize-none focus:ring-0 focus:outline-none"
          placeholder="초안 내용을 편집하세요..."
        />
      </div>
    </div>
  );
}
