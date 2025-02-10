"use client"; 
import { useState } from 'react';
import { Chat } from '@/components/chat';

export default function Home() {
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="w-full max-w-4xl">
        {uploadedFileName && (
          <div className="mt-4 p-2 bg-gray-200 rounded">
            <strong>Uploaded Document:</strong> {uploadedFileName}
          </div>
        )}
        <div className="mt-8">
          <Chat uploadedFileName={uploadedFileName} />
        </div>
      </div>
    </main>
  );
}