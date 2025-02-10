"use client";
import { useState } from 'react'
import { Paperclip, X } from 'lucide-react'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface ChatProps {
  uploadedFileName: string | null;
}

export function Chat({ uploadedFileName }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    setIsLoading(true)
    const userMessage: Message = { role: 'user', content: input }

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage],
          model: 'gpt-4o-mini',
        }),
      })

      if (!response.ok) {
        throw new Error('Network response was not ok')
      }

      const data = await response.json()
      
      setMessages(prevMessages => [
        ...prevMessages,
        userMessage,
        { role: 'assistant', content: data.answer }
      ])
      setInput('')
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setIsUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('/api/chat', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      const data = await response.json()
      console.log('Upload successful:', data)
      setUploadedFile(file.name)
    } catch (error) {
      console.error('Upload error:', error)
    } finally {
      setIsUploading(false)
    }
  }

  const removeUploadedFile = () => {
    setUploadedFile(null)
  }

  return (
    <div className="flex flex-col h-full max-w-2xl mx-auto p-4">
      {uploadedFile && (
        <div className="mb-4 p-3 bg-gray-100 rounded-lg flex items-center gap-2">
          <div className="p-2 bg-white rounded">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M7 18H17V16H7V18Z"
                fill="currentColor"
              />
              <path
                d="M17 14H7V12H17V14Z"
                fill="currentColor"
              />
              <path
                d="M7 10H11V8H7V10Z"
                fill="currentColor"
              />
              <path
                fillRule="evenodd"
                clipRule="evenodd"
                d="M6 2C4.34315 2 3 3.34315 3 5V19C3 20.6569 4.34315 22 6 22H18C19.6569 22 21 20.6569 21 19V9C21 5.13401 17.866 2 14 2H6ZM6 4H13V9H19V19C19 19.5523 18.5523 20 18 20H6C5.44772 20 5 19.5523 5 19V5C5 4.44772 5.44772 4 6 4ZM15 4.10002C16.6113 4.4271 17.9413 5.52906 18.584 7H15V4.10002Z"
                fill="currentColor"
              />
            </svg>
          </div>
          <span className="flex-1">{uploadedFile}</span>
          <button
            onClick={removeUploadedFile}
            className="p-1 hover:bg-gray-200 rounded-full"
          >
            <X className="h-4 w-4" />
            <span className="sr-only">Remove file</span>
          </button>
        </div>
      )}
      <div className="flex-1 overflow-y-auto mb-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`mb-4 ${
              message.role === 'user' ? 'text-right' : 'text-left'
            }`}
          >
            <div
              className={`inline-block p-3 rounded-lg ${
                message.role === 'user'
                  ? 'bg-[#a8e6cf] text-white'
                  : 'bg-gray-200 text-gray-800'
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="flex gap-2 relative">
        <div className="relative flex-1">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask AI..."
            className="w-full p-4 pr-24 rounded-full border border-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-200"
            disabled={isLoading || isUploading}
          />
          <div className="absolute right-2 top-1/2 -translate-y-1/2 flex gap-2">
            <label className="cursor-pointer">
              <input
                type="file"
                className="hidden"
                onChange={handleFileChange}
                accept=".pdf,.docx,.html"
                disabled={isUploading || isLoading}
              />
              <div className="p-2 text-gray-500 hover:text-gray-700 transition-colors">
                <Paperclip className="h-5 w-5" />
                <span className="sr-only">Upload file</span>
              </div>
            </label>
            <button
              type="submit"
              className="p-2 bg-gray-100 hover:bg-gray-200 rounded-full disabled:bg-gray-100 disabled:opacity-50 transition-colors"
              disabled={isLoading || isUploading}
            >
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="transform rotate-90"
              >
                <path
                  d="M12 4L20 20L12 16.5L4 20L12 4Z"
                  fill="currentColor"
                />
              </svg>
              <span className="sr-only">
                {isLoading ? 'Sending...' : isUploading ? 'Uploading...' : 'Send'}
              </span>
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}
