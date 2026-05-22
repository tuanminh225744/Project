📌 Project Management App

Ứng dụng quản lý project & task được xây dựng bằng React Vite + FastAPI + PostgreSQL + Redis, hỗ trợ quản lý dự án, công việc và thành viên với authentication và bộ lọc dữ liệu.

---

✨ Features
📁 Project: CRUD project, xem chi tiết, quản lý member
✅ Task: CRUD task, theo dõi status (Todo / In Progress / Done), priority
🔍 Search & Filter: tìm kiếm task, lọc theo status & priority
👥 Member: thêm/xóa member, phân quyền (owner/member)
🔐 Auth: login/logout, protected routes
🚀 Tech Stack
⚛️ React 18 + TypeScript + Vite
🎨 TailwindCSS + Ant Design
🔀 React Router v6
🧠 Zustand (state management)
📡 Axios (API client)
🐳 Docker Setup (Fullstack Project)

---

📁 Docker Compose Architecture
Frontend (Nginx)
↓
Backend (FastAPI)
↓
PostgreSQL + Redis

---

🚀 Run toàn bộ project

📥 Clone project
git clone <repository-url>

📂 Vào thư mục project
cd <project-folder>

📦 Build & start tất cả services
docker compose up --build

⛔ Stop toàn bộ services
docker compose down
