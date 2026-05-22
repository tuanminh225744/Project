import { Modal, Input, Select, DatePicker } from "antd";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import dayjs from "dayjs";
import { useEffect } from "react";

import { taskSchema, type TaskFormData } from "../schemas/task_schema";

interface TaskModalProps {
  open: boolean;
  mode: "create" | "edit";
  initialValues?: Partial<TaskFormData>;
  onCancel: () => void;
  onSubmit: (data: TaskFormData) => void;
  members?: any[];
}

function TaskModal({
  open,
  mode,
  initialValues,
  onCancel,
  onSubmit,
  members,
}: TaskModalProps) {
  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: initialValues?.title || "",
      description: initialValues?.description || "",
      status: initialValues?.status || "todo",
      priority: initialValues?.priority || "medium",
      assignee_id: initialValues?.assignee_id,
      due_date: initialValues?.due_date,
    },
  });

  useEffect(() => {
    reset({
      title: initialValues?.title || "",
      description: initialValues?.description || "",
      status: initialValues?.status || "todo",
      priority: initialValues?.priority || "medium",
      assignee_id: initialValues?.assignee_id,
      due_date: initialValues?.due_date,
    });
  }, [initialValues, reset]);

  return (
    <Modal
      open={open}
      title={mode === "create" ? "Create Task" : "Edit Task"}
      onCancel={onCancel}
      onOk={handleSubmit(onSubmit)}
      okText={mode === "create" ? "Create" : "Update"}
      style={{
        top: 20,
      }}
    >
      <div className="space-y-4">
        <div>
          <label>Title</label>

          <Controller
            control={control}
            name="title"
            render={({ field }) => (
              <Input {...field} placeholder="Enter title" />
            )}
          />

          {errors.title && (
            <p className="mt-1 text-sm text-red-500">{errors.title.message}</p>
          )}
        </div>

        <div>
          <label>Description</label>

          <Controller
            control={control}
            name="description"
            render={({ field }) => (
              <Input.TextArea
                {...field}
                rows={4}
                placeholder="Enter description"
              />
            )}
          />
        </div>

        <div>
          <label>Status</label>

          <Controller
            control={control}
            name="status"
            render={({ field }) => (
              <Select
                {...field}
                className="w-full"
                options={[
                  { label: "Todo", value: "todo" },
                  { label: "In Progress", value: "in_progress" },
                  { label: "Done", value: "done" },
                ]}
              />
            )}
          />
        </div>

        <div>
          <label>Priority</label>

          <Controller
            control={control}
            name="priority"
            render={({ field }) => (
              <Select
                {...field}
                className="w-full"
                options={[
                  { label: "Low", value: "low" },
                  { label: "Medium", value: "medium" },
                  { label: "High", value: "high" },
                ]}
              />
            )}
          />
        </div>

        <div>
          <label>Assignee</label>

          <Controller
            control={control}
            name="assignee_id"
            render={({ field }) => (
              <Select
                {...field}
                className="w-full"
                placeholder="Select assignee"
                options={members?.map((member) => ({
                  label: member.user?.username,
                  value: member.user?.id,
                }))}
              />
            )}
          />
        </div>

        <div>
          <label>Due Date</label>

          <Controller
            control={control}
            name="due_date"
            render={({ field }) => (
              <DatePicker
                showTime
                className="w-full"
                value={field.value ? dayjs(field.value) : undefined}
                onChange={(date) => field.onChange(date?.toISOString())}
              />
            )}
          />
        </div>
      </div>
    </Modal>
  );
}

export default TaskModal;
