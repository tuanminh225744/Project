import { useState } from "react";
import { Alert, Button, Card, Form, Input, Typography } from "antd";
import { Link, useNavigate } from "react-router-dom";
import { loginApi } from "../services/auth_service";

type LoginFormValues = {
  username: string;
  password: string;
};

export default function Login() {
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (values: LoginFormValues) => {
    setError("");
    setIsSubmitting(true);

    try {
      const response = await loginApi(values);

      localStorage.setItem("accessToken", response.access_token);
      localStorage.setItem("refreshToken", response.refresh_token);

      navigate("/dashboard", { replace: true });
    } catch {
      setError("Username hoặc password không đúng.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-100 px-4 py-8">
      <Card className="w-full max-w-md shadow-md">
        <div className="mb-6">
          <Typography.Text className="text-xs font-semibold uppercase tracking-wide text-blue-600">
            Project Management
          </Typography.Text>
          <Typography.Title level={2} className="!mb-0 !mt-2">
            Đăng nhập
          </Typography.Title>
        </div>

        <Form<LoginFormValues> layout="vertical" onFinish={handleSubmit} requiredMark={false}>
          <Form.Item
            label="Username"
            name="username"
            rules={[{ required: true, message: "Vui lòng nhập username." }]}
          >
            <Input size="large" autoComplete="username" placeholder="Nhập username" />
          </Form.Item>

          <Form.Item
            label="Password"
            name="password"
            rules={[{ required: true, message: "Vui lòng nhập password." }]}
          >
            <Input.Password
              size="large"
              autoComplete="current-password"
              placeholder="Nhập password"
            />
          </Form.Item>

          {error ? <Alert className="mb-4" type="error" message={error} showIcon /> : null}

          <Button
            block
            size="large"
            type="primary"
            htmlType="submit"
            loading={isSubmitting}
          >
            Đăng nhập
          </Button>
        </Form>

        <Typography.Paragraph className="!mb-0 !mt-4 text-center">
          Chưa có tài khoản? <Link to="/register">Đăng ký</Link>
        </Typography.Paragraph>
      </Card>
    </main>
  );
}
