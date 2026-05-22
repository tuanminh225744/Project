📌 Project Management App

Ứng dụng quản lý project & task được xây dựng bằng React Vite + FastAPI + PostgreSQL + Redis, hỗ trợ quản lý dự án, công việc và thành viên với authentication và bộ lọc dữ liệu.

---

✨ Features<br>
📁 Project: CRUD project, xem chi tiết, quản lý member<br>
✅ Task: CRUD task, theo dõi status (Todo / In Progress / Done), priority<br>
🔍 Search & Filter: tìm kiếm task, lọc theo status & priority<br>
👥 Member: thêm/xóa member, phân quyền (owner/member)<br>
🔐 Auth: login/logout, protected routes<br>
🚀 Tech Stack<br>
⚛️ React 18 + TypeScript + Vite<br>
🎨 TailwindCSS + Ant Design<br>
🔀 React Router v6<br>
🧠 Zustand (state management)<br>
📡 Axios (API client)<br>
🐳 Docker Setup (Fullstack Project)<br>

---

📁 Docker Compose Architecture<br>
Frontend (Nginx)<br>
↓<br>
Backend (FastAPI)<br>
↓<br>
PostgreSQL + Redis<br>

---

🚀 Run toàn bộ project<br>

📥 Clone project<br>
git clone https://github.com/tuanminh225744/Project.git<br>

📂 Vào thư mục project<br>
cd Project<br>

📦 Build & start tất cả services<br>
docker compose up --build<br>

⛔ Stop toàn bộ services<br>
docker compose down<br>
