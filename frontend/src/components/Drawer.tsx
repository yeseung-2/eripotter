'use client';

import { useEffect } from 'react';
import { X } from 'lucide-react';

interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  question: {
    item_desc?: string;
    metric_desc?: string;
    data_source?: string;
    data_period?: string;
    data_method?: string;
    data_detail?: string;
  };
}

export function Drawer({ isOpen, onClose, question }: DrawerProps) {
  // Drawer 열릴 때 배경 스크롤 방지
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    // 컴포넌트 언마운트 시 스크롤 복원
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 z-40 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Drawer */}
      <div 
        className={`fixed right-0 top-0 h-full w-full max-w-2xl bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-in-out border-l border-gray-200 ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-gray-50">
            <h2 className="text-lg font-semibold text-gray-900">항목 상세 안내</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-200 rounded-full transition-colors duration-200"
              aria-label="닫기"
            >
              <X className="w-5 h-5 text-gray-600" />
            </button>
          </div>
          
          {/* Content */}
          <div className="flex-1 overflow-y-auto">
            <div className="p-6 space-y-6">
              {question.item_desc && (
                <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <label className="block text-sm font-semibold text-gray-800 mb-2">
                    📋 항목 설명
                  </label>
                  <p className="text-gray-700 leading-relaxed text-sm">
                    {question.item_desc}
                  </p>
                </div>
              )}
              
              {question.metric_desc && (
                <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <label className="block text-sm font-semibold text-gray-800 mb-2">
                    📊 성과 점검
                  </label>
                  <p className="text-gray-700 leading-relaxed text-sm">
                    {question.metric_desc}
                  </p>
                </div>
              )}
              
              {question.data_source && (
                <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <label className="block text-sm font-semibold text-gray-800 mb-2">
                    🔗 데이터 원천
                  </label>
                  <p className="text-gray-700 leading-relaxed text-sm">
                    {question.data_source}
                  </p>
                </div>
              )}
              
              {question.data_period && (
                <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <label className="block text-sm font-semibold text-gray-800 mb-2">
                    📅 데이터 기간
                  </label>
                  <p className="text-gray-700 leading-relaxed text-sm">
                    {question.data_period}
                  </p>
                </div>
              )}
              
              {question.data_method && (
                <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <label className="block text-sm font-semibold text-gray-800 mb-2">
                    🧮 데이터 산식
                  </label>
                  <p className="text-gray-700 leading-relaxed text-sm">
                    {question.data_method}
                  </p>
                </div>
              )}
              
              {question.data_detail && (
                <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <label className="block text-sm font-semibold text-gray-800 mb-2">
                    📏 데이터 범위
                  </label>
                  <p className="text-gray-700 leading-relaxed text-sm">
                    {question.data_detail}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
