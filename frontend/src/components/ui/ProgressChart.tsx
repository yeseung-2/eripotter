"use client";

interface ProgressChartProps {
  total: number;
  completed: number;
  inProgress: number;
  pending: number;
}

export default function ProgressChart({ total, completed, inProgress, pending }: ProgressChartProps) {
  if (total === 0) return null;

  const completedPercent = (completed / total) * 100;
  const inProgressPercent = (inProgress / total) * 100;
  const pendingPercent = (pending / total) * 100;

  return (
    <div className="flex items-center space-x-4">
      {/* 파이차트 */}
      <div className="relative w-16 h-16">
        <svg className="w-16 h-16 transform -rotate-90" viewBox="0 0 36 36">
          {/* 배경 원 */}
          <circle
            cx="18"
            cy="18"
            r="16"
            fill="none"
            className="stroke-gray-200"
            strokeWidth="3"
          />
          
          {/* 완료된 부분 */}
          {completed > 0 && (
            <circle
              cx="18"
              cy="18"
              r="16"
              fill="none"
              className="stroke-green-500"
              strokeWidth="3"
              strokeDasharray={`${completedPercent * 1.13} 100`}
              strokeDashoffset="0"
            />
          )}
          
          {/* 진행 중인 부분 */}
          {inProgress > 0 && (
            <circle
              cx="18"
              cy="18"
              r="16"
              fill="none"
              className="stroke-yellow-500"
              strokeWidth="3"
              strokeDasharray={`${inProgressPercent * 1.13} 100`}
              strokeDashoffset={`-${completedPercent * 1.13}`}
            />
          )}
          
          {/* 대기 중인 부분 */}
          {pending > 0 && (
            <circle
              cx="18"
              cy="18"
              r="16"
              fill="none"
              className="stroke-gray-400"
              strokeWidth="3"
              strokeDasharray={`${pendingPercent * 1.13} 100`}
              strokeDashoffset={`-${(completedPercent + inProgressPercent) * 1.13}`}
            />
          )}
        </svg>
        
        {/* 중앙 텍스트 */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-xs font-medium text-gray-700">
            {Math.round(completedPercent)}%
          </span>
        </div>
      </div>

      {/* 범례 */}
      <div className="flex flex-col space-y-1 text-xs">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          <span className="text-gray-600">완료: {completed}개</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
          <span className="text-gray-600">진행중: {inProgress}개</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
          <span className="text-gray-600">대기: {pending}개</span>
        </div>
      </div>
    </div>
  );
}
