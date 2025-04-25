

# 🧠 AI Chatbot with Document Upload – Project Documentation

## 📦 Project Overview

This project is an **AI-powered RAG (Retrieval-Augmented Generation) Chatbot** that:
- Allows users to upload `.pdf`, `.docx`, or `.html` documents
- Uses LangChain + ChromaDB to semantically index and retrieve information from uploaded documents
- Returns intelligent answers based on context from uploaded files and prior conversation history
- Comes with a **Next.js + ShadCN frontend** for an elegant, modern UI

---

## 🛠 Backend – FastAPI + LangChain + ChromaDB

### 🧩 Key Technologies:
- **FastAPI**: REST API framework
- **LangChain**: RAG chain integration using LLMs
- **ChromaDB**: Vector database for storing document embeddings
- **SQLite**: Lightweight database for logs and metadata
- **Pydantic**: Data validation
- **Logging**: Logs queries and responses to `app.log`

---

### 📁 API Endpoints

#### 1. **Chat with AI**
```http
POST /chat
```
**Payload** (`QueryInput`):
```json
{
  "session_id": "optional-string",
  "question": "What does this document say about diabetes?",
  "model": "groq" 
}
```
**Returns**:
```json
{
  "answer": "The document states that diabetes is a chronic condition...",
  "session_id": "uuid-generated-if-missing",
  "model": "groq"
}
```

#### 2. **Upload Document**
```http
POST /upload-doc
```
**Form Data**:
- `file`: `.pdf`, `.docx`, or `.html`

**Returns**:
```json
{
  "message": "File XYZ.pdf has been successfully uploaded and indexed.",
  "file_id": "abc123"
}
```

#### 3. **List Uploaded Documents**
```http
GET /list-docs?skip=0&limit=10
```
**Returns**:
```json
[
  {
    "file_id": "abc123",
    "filename": "XYZ.pdf",
    "uploaded_at": "2024-04-20T15:00:00"
  }
]
```

#### 4. **Delete Document**
```http
POST /delete-doc
```
**Payload**:
```json
{
  "file_id": "abc123"
}
```
**Returns**:
```json
{
  "message": "Successfully deleted document with file_id abc123 from the system."
}
```

---

### 🗃 Database Schema (SQLite)

- `logs`: stores query/response pairs with timestamps
- `documents`: stores uploaded document metadata

---

## 🌐 Frontend – Next.js + Tailwind + ShadCN UI

### 🧩 Stack:
- **Next.js (App Router)**
- **TailwindCSS**: Styling
- **ShadCN UI**: Pre-built, accessible components
- **Lucide Icons**: For upload/send icons

---

### 🖥 Key Features:

- **Chat UI**:
  - Input with `Enter` or send icon to ask questions
  - User messages in **green**
  - Bot replies in default theme
  - Auto-scrolls and clears input after submission

- **Document Upload UI**:
  - Upload `.pdf`, `.docx`, `.html` files
  - Positioned **upload icon inside** input box (right side)
  - Shows file upload status

- **Sidebar**:
  - Lists uploaded documents
  - Optionally allow deletion via icon

---

### 📁 Suggested Frontend Folder Structure:
```
/app
  ├── layout.tsx
  ├── page.tsx
  └── components/
      ├── ChatBox.tsx
      ├── ChatBubble.tsx
      ├── Sidebar.tsx
      └── UploadButton.tsx
/styles
  └── tailwind.css
```

---

### 🔌 API Integration (ChatBox.tsx example)

```tsx
const sendQuery = async () => {
  const res = await fetch("http://localhost:8000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question: input,
      session_id,
      model: "groq",
    }),
  });
  const data = await res.json();
  setMessages((prev) => [...prev, { type: "bot", text: data.answer }]);
};
```

---

## 🚀 Deployment

### 1. **EC2 Setup for Docker**
```bash
sudo apt-get update -y
sudo apt-get upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
newgrp docker
```

### 2. **Self-Hosted Runner Setup**
```bash
# From GitHub → Settings → Actions → Runners
./config.sh --url https://github.com/your/repo --token YOUR_TOKEN
./run.sh
```

### 3. **GitHub Secrets (for ECR + Deploy)**

| Key                     | Value                                              |
|-------------------------|----------------------------------------------------|
| AWS_ACCESS_KEY_ID       | IAM access key                                     |
| AWS_SECRET_ACCESS_KEY   | IAM secret key                                     |
| AWS_REGION              | `us-east-1`                                        |
| AWS_ECR_LOGIN_URI       | `566373416292.dkr.ecr.ap-south-1.amazonaws.com`    |
| ECR_REPOSITORY_NAME     | `simple-app`                                       |



---

