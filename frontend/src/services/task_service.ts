import axiosInstance from "../api";
import { taskSchema } from "../schemas/task_schema";
import { z } from "zod";

export interface Task {
  id: number;
  title: string;
  description?: string | null;
  status: "todo" | "in_progress" | "done";
  priority: "low" | "medium" | "high";
  assignee_id?: number | null;
  due_date?: string | null;

  project_id: number;
  created_by: number;

  created_at: string;
  updated_at?: string | null;
}

export interface CreateTaskPayload {
  title: string;
  description?: string;
  status?: "todo" | "in_progress" | "done";
  priority?: "low" | "medium" | "high";
  assignee_id?: number;
  due_date?: string;

  project_id: number;
  created_by?: number;
}

export type UpdateTaskFormData = z.infer<typeof taskSchema>;

export type CreateTaskFormData = z.infer<typeof taskSchema>;

export interface UpdateTaskPayload {
  title?: string;
  description?: string;
  status?: "todo" | "in_progress" | "done";
  priority?: "low" | "medium" | "high";
  assignee_id?: number;
  due_date?: string;
}

// Get all tasks
export const getTasksApi = async () => {
  return axiosInstance.get<Task[], Task[]>("/tasks/");
};

// Get tasks by project id
export const getTasksByProjectApi = async (projectId: number | string) => {
  return axiosInstance.get<Task[], Task[]>(`/tasks/project/${projectId}`);
};

// Get task detail
export const getTaskByIdApi = async (taskId: number) => {
  return axiosInstance.get<Task, Task>(`/tasks/${taskId}`);
};

// Create task
export const createTaskApi = async (payload: CreateTaskPayload) => {
  return axiosInstance.post<Task, Task>("/tasks/", payload);
};

// Update task
export const updateTaskApi = async (
  taskId: number,
  payload: UpdateTaskPayload,
) => {
  return axiosInstance.put<Task, Task>(`/tasks/${taskId}`, payload);
};

// Delete task
export const deleteTaskApi = async (taskId: number) => {
  return axiosInstance.delete(`/tasks/${taskId}`);
};
