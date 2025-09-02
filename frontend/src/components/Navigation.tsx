'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import Image from 'next/image';
import { cn } from '@/lib/utils';

interface NavigationProps {
  userType: 'supplier' | 'customer';
}

const supplierMenuItems = [
  { href: '/assessment', label: 'Assessment' },
  { href: '/chat', label: 'Chat' },
  { href: '/data-sharing-approval', label: 'Data Sharing Approval' },
  { href: '/data-upload', label: 'Data Upload' },
  { href: '/report', label: 'Report' },
];

const customerMenuItems = [
  { href: '/data-sharing-request', label: 'Data Sharing Request' },
  { href: '/monitoring', label: 'Monitoring' },
];

export default function Navigation({ userType }: NavigationProps) {
  const pathname = usePathname();
  const menuItems = userType === 'supplier' ? supplierMenuItems : customerMenuItems;

  return (
    <div className="w-64 h-screen bg-white border-r border-gray-200 flex flex-col shadow-lg">
      {/* Logo Section */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex justify-center">
          <div className="w-16 h-16 relative">
            <Image
              src="/logo.png"
              alt="ERI Logo"
              fill
              className="object-contain"
            />
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
                "flex items-center px-4 py-3 rounded-lg text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-all duration-200 border-l-4 border-transparent",
                pathname === item.href && "bg-gray-50 text-gray-900 border-l-blue-600 font-medium"
              )}
            >
              <span className="font-medium text-sm">{item.label}</span>
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
