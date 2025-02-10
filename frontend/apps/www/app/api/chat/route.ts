import { z } from "zod"
import { NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Validate the incoming message format
const MessageSchema = z.object({
  messages: z.array(z.object({
    role: z.enum(['user', 'assistant']),
    content: z.string()
  })),
  model: z.string().optional(),
  session_id: z.string().optional()
});

// Validate the incoming file upload format
const FileUploadSchema = z.object({
  file: z.instanceof(File).optional(),
});

export async function POST(req: Request) {
  try {
    // Check if the request is a file upload by checking the content type
    const contentType = req.headers.get('content-type') || '';
    
    if (contentType.includes('multipart/form-data')) {
      // Handle file upload
      const formData = await req.formData();
      const file = formData.get('file');

      if (!file) {
        return NextResponse.json(
          { error: 'No file provided' },
          { status: 400 }
        );
      }

      // Forward the request to FastAPI backend
      const apiFormData = new FormData();
      apiFormData.append('file', file);

      const response = await fetch(`${API_URL}/upload-doc`, {
        method: 'POST',
        body: apiFormData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to upload file');
      }

      const data = await response.json();
      return NextResponse.json(data);
    } else {
      // Handle chat messages
      const json = await req.json();
      
      // Validate the request body
      const validatedData = MessageSchema.parse(json);
      const lastMessage = validatedData.messages[validatedData.messages.length - 1];

      // Make request to FastAPI backend
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: lastMessage.content,
          session_id: validatedData.session_id || crypto.randomUUID(),
          model: validatedData.model || 'gpt-4o-mini'
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to get response from backend');
      }

      const data = await response.json();
      
      return new Response(JSON.stringify({ answer: data.answer }), {
        headers: { 'Content-Type': 'application/json' },
      });
    }
  } catch (error) {
    console.error('API Error:', error);
    return new Response(
      JSON.stringify({ 
        error: error instanceof Error ? error.message : 'Internal Server Error'
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
}

const SYSTEM_PROMPT = `You are a helpful AI assistant demonstrating the shadcn-chatbot-kit component library. You aim to be helpful and knowledgeable while showing off the UI capabilities of the chat interface.

Important guidelines:
1. Only use tools when they are specifically needed to complete a task or explicitly requested. Never call tools automatically or in response to random input.

2. If you receive unclear input or random text (e.g., "asdfgh"), respond politely asking for clarification instead of making assumptions or calling tools.

3. Keep responses concise and focused to demonstrate good chat UI practices. Use appropriate formatting when helpful (bold, italic, lists).

4. Refuse any requests for harmful content, generation of malicious code, or private information. Explain why such requests cannot be fulfilled.

5. You can engage in casual conversation, answer questions, help with tasks, and provide information about the component library itself when asked.

Sample appropriate responses:
- For "hi": "Hello! How can I help you today?"
- For "asdfgh": "I didn't quite understand that. Could you please rephrase or clarify what you're looking for?"
- For "what's the weather like?": "I can check the weather for you. Which city would you like to know about?"

Remember: You're here to be helpful while demonstrating good chatbot UI/UX practices. Keep responses natural but professional.`
