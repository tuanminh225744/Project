import { z } from "zod";

export const projectPriorityValues = ["low", "medium", "high"] as const;
export const projectStatusValues = ["todo", "in_progress", "done"] as const;

export const createProjectSchema = z.object({
  name: z.string().trim().min(1, "Vui lòng nhập tên project."),
  description: z.string().trim().optional(),
  priority: z.enum(projectPriorityValues, "Vui lòng chọn priority hợp lệ."),
  due_date: z
    .string()
    .min(1, "Vui lòng chọn due date.")
    .regex(
      /^\d{4}-\d{2}-\d{2}$/,
      "Due date phải đúng định dạng ngày tháng năm.",
    ),
});

export const updateProjectSchema = z.object({
  name: z.string().trim().min(1, "Vui lòng nhập tên project."),
  description: z.string().trim().optional(),
  priority: z.enum(projectPriorityValues, "Vui lòng chọn priority hợp lệ."),
  due_date: z
    .string()
    .min(1, "Vui lòng chọn due date.")
    .regex(
      /^\d{4}-\d{2}-\d{2}$/,
      "Due date phải đúng định dạng ngày tháng năm.",
    ),
  status: z
    .enum(projectStatusValues, "Vui lòng chọn status hợp lệ.")
    .optional(),
});

export type CreateProjectFormValues = z.infer<typeof createProjectSchema>;
export type UpdateProjectFormValues = z.infer<typeof updateProjectSchema>;
