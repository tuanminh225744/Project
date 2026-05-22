FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./

# Sử dụng npm ci thay vì npm install để cài đặt chính xác theo package-lock.json và nhanh hơn
RUN npm install

COPY . .

# Biên dịch ứng dụng thành các file tĩnh (HTML, JS, CSS)
RUN npm run build

FROM nginx:1.25-alpine

# Copy các file tĩnh từ giai đoạn build vào thư mục mặc định của Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy file cấu hình Nginx tùy chỉnh (giúp tránh lỗi 404 khi reload trang nếu có dùng React Router)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Nginx chạy mặc định ở cổng 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]