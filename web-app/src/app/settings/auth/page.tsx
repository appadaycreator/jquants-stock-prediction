'use client';

import React from 'react';
import AuthSettings from '@/components/auth/AuthSettings';

export default function AuthSettingsPage() {
  return (
    <div className="container mx-auto py-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold">認証設定</h1>
          <p className="text-gray-600 mt-2">
            J-Quants APIへの安全な認証設定を行います。
          </p>
        </div>
        
        <AuthSettings />
      </div>
    </div>
  );
}
