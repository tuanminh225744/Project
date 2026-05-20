import { z } from "zod";

export const loginSchema = z.object({
  username: z.string().min(1, "Vui lòng nhập username."),
  password: z.string().min(1, "Vui lòng nhập password."),
});

export const registerSchema = z
  .object({
    username: z.string().min(1, "Vui lòng nhập username."),
    email: z.email("Email không hợp lệ.").min(1, "Vui lòng nhập email."),
    password: z
      .string()
      .min(1, "Vui lòng nhập password.")
      .min(6, "Password phải có ít nhất 6 ký tự."),
    confirmPassword: z.string().min(1, "Vui lòng nhập lại password."),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Password nhập lại không khớp.",
    path: ["confirmPassword"],
  });

export type LoginFormValues = z.infer<typeof loginSchema>;
export type RegisterFormValues = z.infer<typeof registerSchema>;
