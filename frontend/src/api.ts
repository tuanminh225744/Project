import axios from "axios";
import type { AxiosInstance, InternalAxiosRequestConfig } from "axios";

// Giả sử bạn lưu token trong localStorage hoặc cookies
const getLocalAccessToken = () => localStorage.getItem("accessToken");
const getLocalRefreshToken = () => localStorage.getItem("refreshToken");
const setLocalAccessToken = (token: string) =>
  localStorage.setItem("accessToken", token);

// Khởi tạo Axios Instance
const apiUrl = import.meta.env.VITE_API_URL;
const axiosInstance: AxiosInstance = axios.create({
  baseURL: apiUrl,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

// Biến quản lý trạng thái Refresh Token
let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

// Hàm thêm các request bị hoãn vào hàng đợi
const subscribeTokenRefresh = (cb: (token: string) => void) => {
  refreshSubscribers.push(cb);
};

// Hàm chạy lại các request trong hàng đợi sau khi đã có token mới
const onRefreshed = (token: string) => {
  refreshSubscribers.map((cb) => cb(token));
  refreshSubscribers = [];
};

// Tự động đính kèm token
axiosInstance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getLocalAccessToken();
    if (token && config.headers) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

axiosInstance.interceptors.response.use(
  (response) => {
    return response.data;
  },
  async (error) => {
    const originalRequest = error.config;
    const refreshToken = getLocalRefreshToken();

    // Nếu không có config hoặc không phải lỗi 401, bỏ qua
    if (!error.response || error.response.status !== 401) {
      return Promise.reject(error);
    }

    // Nếu request ban đầu không có token hoặc không có refresh token,
    // giữ nguyên lỗi 401 từ backend thay vì gọi refresh rồi làm nhiễu status.
    if (!getLocalAccessToken() || !refreshToken) {
      return Promise.reject(error);
    }

    // Trường hợp URL chính là API refresh token mà vẫn lỗi 401 -> Refresh token hết hạn -> Logout luôn
    if (originalRequest.url.includes("/auth/refresh")) {
      handleLogout();
      return Promise.reject(error);
    }

    // Nếu chưa có tiến trình refresh token nào đang chạy
    if (!isRefreshing) {
      isRefreshing = true;

      try {
        // Gọi API refresh token (Sử dụng một axios instance gốc/mới để tránh bị dính interceptor cũ)
        const res = await axios.post(`${apiUrl}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const newAccessToken = res.data.access_token;
        setLocalAccessToken(newAccessToken);

        isRefreshing = false;
        onRefreshed(newAccessToken);

        // Thực thi lại chính request bị lỗi ban đầu với token mới
        originalRequest.headers["Authorization"] = `Bearer ${newAccessToken}`;
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        isRefreshing = false;
        handleLogout();
        return Promise.reject(refreshError);
      }
    }

    const retryOriginalRequest = new Promise((resolve) => {
      subscribeTokenRefresh((token: string) => {
        originalRequest.headers["Authorization"] = `Bearer ${token}`;
        resolve(axiosInstance(originalRequest));
      });
    });

    return retryOriginalRequest;
  },
);

const handleLogout = () => {
  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
  window.location.href = "/login";
};

export default axiosInstance;
