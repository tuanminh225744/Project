import { zodResolver } from "@hookform/resolvers/zod";
import { Alert, Button, Card, Form, Input, Typography } from "antd";
import { Controller, useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { loginSchema, type LoginFormValues } from "../schemas/auth_schema";
import { useAuthStore } from "../store/useAuthStore";

export default function Login() {
  const navigate = useNavigate();
  const { error, isLoading, login, clearError } = useAuthStore();
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: "",
      password: "",
    },
  });

  const onSubmit = async (values: LoginFormValues) => {
    try {
      await login(values);
      navigate("/project", { replace: true });
    } catch {
      // Error message is managed by the global auth store.
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

        <Form
          layout="vertical"
          onSubmitCapture={handleSubmit(onSubmit)}
          onChange={clearError}
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
            label="Password"
            validateStatus={errors.password ? "error" : undefined}
            help={errors.password?.message}
          >
            <Controller
              name="password"
              control={control}
              render={({ field }) => (
                <Input.Password
                  {...field}
                  size="large"
                  autoComplete="current-password"
                  placeholder="Nhập password"
                />
              )}
            />
          </Form.Item>

          {error ? (
            <Alert className="mb-4" type="error" message={error} showIcon />
          ) : null}

          <Button
            block
            size="large"
            type="primary"
            htmlType="submit"
            loading={isLoading}
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
