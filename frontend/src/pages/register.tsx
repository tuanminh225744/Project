import { useState } from "react";
import { Alert, Button, Card, Form, Input, Typography } from "antd";
import { Link, useNavigate } from "react-router-dom";
import { registerApi } from "../services/auth_service";

type RegisterFormValues = {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
};

export default function Register() {
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (values: RegisterFormValues) => {
    setError("");
    setIsSubmitting(true);

    try {
      await registerApi({
        username: values.username,
        email: values.email,
        password: values.password,
      });

      navigate("/login", { replace: true });
    } catch {
      setError("Không thể đăng ký tài khoản. Vui lòng kiểm tra lại thông tin.");
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
            Đăng ký
          </Typography.Title>
        </div>

        <Form<RegisterFormValues> layout="vertical" onFinish={handleSubmit} requiredMark={false}>
          <Form.Item
            label="Username"
            name="username"
            rules={[{ required: true, message: "Vui lòng nhập username." }]}
          >
            <Input size="large" autoComplete="username" placeholder="Nhập username" />
          </Form.Item>

          <Form.Item
            label="Email"
            name="email"
            rules={[
              { required: true, message: "Vui lòng nhập email." },
              { type: "email", message: "Email không hợp lệ." },
            ]}
          >
            <Input size="large" autoComplete="email" placeholder="Nhập email" />
          </Form.Item>

          <Form.Item
            label="Password"
            name="password"
            rules={[
              { required: true, message: "Vui lòng nhập password." },
              { min: 6, message: "Password phải có ít nhất 6 ký tự." },
            ]}
            hasFeedback
          >
            <Input.Password size="large" autoComplete="new-password" placeholder="Nhập password" />
          </Form.Item>

          <Form.Item
            label="Nhập lại password"
            name="confirmPassword"
            dependencies={["password"]}
            hasFeedback
            rules={[
              { required: true, message: "Vui lòng nhập lại password." },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue("password") === value) {
                    return Promise.resolve();
                  }

                  return Promise.reject(new Error("Password nhập lại không khớp."));
                },
              }),
            ]}
          >
            <Input.Password
              size="large"
              autoComplete="new-password"
              placeholder="Nhập lại password"
            />
          </Form.Item>

          {error ? <Alert className="mb-4" type="error" message={error} showIcon /> : null}

          <Button block size="large" type="primary" htmlType="submit" loading={isSubmitting}>
            Đăng ký
          </Button>
        </Form>

        <Typography.Paragraph className="!mb-0 !mt-4 text-center">
          Đã có tài khoản? <Link to="/login">Đăng nhập</Link>
        </Typography.Paragraph>
      </Card>
    </main>
  );
}
