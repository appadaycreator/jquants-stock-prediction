'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Sidebar() {
  const pathname = usePathname();

  const navigation = [
    { name: 'ホーム', href: '/', icon: '🏠' },
    { name: '今日の指示', href: '/today', icon: '📅' },
    { name: 'レポート', href: '/reports', icon: '📊' },
    { name: '設定', href: '/settings', icon: '⚙️' },
    { name: 'ヘルプ', href: '/usage', icon: '❓' },
  ];

  const additionalFeatures = [
    { name: '個人投資', href: '/personal-investment', icon: '💼' },
    { name: 'レポート', href: '/reports', icon: '📈' },
    { name: '分析状況', href: '/analysis-progress', icon: '🔄' },
  ];

  return (
    <nav className="hidden lg:block fixed left-0 top-0 h-full w-64 bg-white border-r border-gray-200 z-40">
      <div className="p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">
          J-Quants株価予測
        </h2>
        
        <div className="space-y-2">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                <span className="font-medium">{item.name}</span>
              </Link>
            );
          })}
          
          <div className="border-t border-gray-200 my-4"></div>
          
          {additionalFeatures.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors ${
                  isActive ? 'bg-gray-50' : ''
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                <span className="font-medium">{item.name}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
