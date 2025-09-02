'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import Image from 'next/image';
import { cn } from '@/lib/utils';

interface NavigationProps {
  userType: 'supplier' | 'customer';
}

const supplierMenuItems = [
  { href: '/assessment', label: 'Assessment', icon: '📊' },
  { href: '/chat', label: 'Chat', icon: '💬' },
  { href: '/data-sharing-approval', label: 'Data Sharing Approval', icon: '✅' },
  { href: '/data-upload', label: 'Data Upload', icon: '📤' },
  { href: '/mypage', label: 'My Page', icon: '👤' },
  { href: '/report', label: 'Report', icon: '📋' },
];

const customerMenuItems = [
  { href: '/data-sharing-request', label: 'Data Sharing Request', icon: '📥' },
  { href: '/mypage', label: 'My Page', icon: '👤' },
  { href: '/monitoring', label: 'Monitoring', icon: '📊' },
];

export default function Navigation({ userType }: NavigationProps) {
  const pathname = usePathname();
  const menuItems = userType === 'supplier' ? supplierMenuItems : customerMenuItems;

  return (
    <div className="w-64 h-screen bg-white border-r border-gray-200 flex flex-col shadow-lg">
      {/* Logo Section */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 relative">
            <Image
              src="/logo.png"
              alt="ERI Logo"
              fill
              className="object-contain"
            />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">ERI</h1>
            <p className="text-xs text-gray-600">Environmental Risk Intelligence</p>
          </div>
        </div>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 p-4">
        <div className="space-y-2">
          {menuItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-blue-50 hover:text-blue-700 transition-colors duration-200",
                pathname === item.href && "bg-blue-100 text-blue-700 border-r-2 border-blue-500"
              )}
            >
              <span className="text-lg">{item.icon}</span>
              <span className="font-medium">{item.label}</span>
            </Link>
          ))}
        </div>
      </nav>

      {/* User Type Indicator */}
      <div className="p-4 border-t border-gray-200">
        <div className="text-center">
          <span className={cn(
            "inline-flex items-center px-3 py-1 rounded-full text-xs font-medium",
            userType === 'supplier' 
              ? "bg-green-100 text-green-800" 
              : "bg-blue-100 text-blue-800"
          )}>
            {userType === 'supplier' ? '협력사' : '고객사'}
          </span>
        </div>
      </div>
    </div>
  );
}
