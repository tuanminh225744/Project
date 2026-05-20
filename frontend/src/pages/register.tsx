import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { Alert, Button, Card, Form, Input, Typography } from "antd";
import { Controller, useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import {
  registerSchema,
  type RegisterFormValues,
} from "../schemas/auth_schema";
import { registerApi } from "../services/auth_service";

export default function Register() {
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      username: "",
      email: "",
      password: "",
      confirmPassword: "",
    },
  });

  const onSubmit = async (values: RegisterFormValues) => {
    setError("");

    try {
      await registerApi({
        username: values.username,
        email: values.email,
        password: values.password,
      });

      navigate("/login", { replace: true });
    } catch {
      setError("Không thể đăng ký tài khoản. Vui lòng kiểm tra lại thông tin.");
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

        <Form
          layout="vertical"
          onSubmitCapture={handleSubmit(onSubmit)}
          requiredMark={false}
        >
          <Form.Item
            label="Username"
            validateStatus={errors.username ? "error" : undefined}
            help={errors.username?.message}
          >
            <Controller
              name="username"
              control={control}
              render={({ field }) => (
                <Input
                  {...field}
                  size="large"
                  autoComplete="username"
                  placeholder="Nhập username"
                />
              )}
            />
          </Form.Item>

          <Form.Item
            label="Email"
            validateStatus={errors.email ? "error" : undefined}
            help={errors.email?.message}
          >
            <Controller
              name="email"
              control={control}
              render={({ field }) => (
                <Input
                  {...field}
                  size="large"
                  autoComplete="email"
                  placeholder="Nhập email"
                />
              )}
            />
          </Form.Item>

          <Form.Item
            label="Password"
            validateStatus={errors.password ? "error" : undefined}
            help={errors.password?.message}
            hasFeedback
          >
            <Controller
              name="password"
              control={control}
              render={({ field }) => (
                <Input.Password
                  {...field}
                  size="large"
                  autoComplete="new-password"
                  placeholder="Nhập password"
                />
              )}
            />
          </Form.Item>

          <Form.Item
            label="Nhập lại password"
            validateStatus={errors.confirmPassword ? "error" : undefined}
            help={errors.confirmPassword?.message}
            hasFeedback
          >
            <Controller
              name="confirmPassword"
              control={control}
              render={({ field }) => (
                <Input.Password
                  {...field}
                  size="large"
                  autoComplete="new-password"
                  placeholder="Nhập lại password"
                />
              )}
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
