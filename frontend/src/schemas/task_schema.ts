import { z } from "zod";

export const taskSchema = z.object({
  title: z.string().min(1, "Title is required"),
  description: z.string().optional(),

  status: z.enum(["todo", "in_progress", "done"]),

  priority: z.enum(["low", "medium", "high"]),

  assignee_id: z.coerce.number().optional(),

  due_date: z.string().optional(),
});

export type TaskFormData = z.input<typeof taskSchema>;
