'use client';

interface FabReloadProps {
  onRefresh: () => void;
  isLoading?: boolean;
}

export default function FabReload({ onRefresh, isLoading = false }: FabReloadProps) {
  return (
    <button
      onClick={onRefresh}
      disabled={isLoading}
      className="fixed bottom-20 right-4 bg-blue-600 text-white rounded-full p-4 shadow-lg hover:bg-blue-700 transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed z-40 md:hidden"
      aria-label="データを更新"
    >
      {isLoading ? (
        <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
      ) : (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      )}
    </button>
  );
}
