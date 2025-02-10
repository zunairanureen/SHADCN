import { ChatMessage } from "@/registry/default/ui/chat-message"

export default function ChatMessageCustomStylingDemo() {
  return (
    <div className="w-full space-y-4">
      <ChatMessage
        id="1"
        role="user"
        content="This message will be red"
        className="bg-red-500 text-white"
      />
      <ChatMessage
        id="2"
        role="assistant"
        content="This message will be outlined"
        className="bg-transparent border"
      />
    </div>
  )
}
