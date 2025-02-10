"use client";

import { useState } from 'react';
import { Chat } from '@/components/chat';
import { UploadButton } from '@/components/upload-button';

export default function Home() {
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);

  const handleFileUpload = (fileName: string) => {
    setUploadedFileName(fileName); // Update the state with the uploaded file name
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 bg-gray-100">
      <div className="w-full max-w-4xl">
        <UploadButton onFileUpload={handleFileUpload} />
        {uploadedFileName && (
          <div className="mt-4 p-2 bg-gray-200 rounded">
            <strong>Uploaded Document:</strong> {uploadedFileName}
          </div>
        )}
        <div className="mt-8">
          <Chat uploadedFileName={uploadedFileName} /> {/* Pass the file name to Chat */}
        </div>
      </div>
    </main>
  );
}