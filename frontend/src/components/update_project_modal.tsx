import { Modal, Input, Select, DatePicker } from "antd";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import dayjs from "dayjs";

import { updateProjectSchema } from "../schemas/project_schema";
import { type UpdateProjectFormValues } from "../schemas/project_schema";

interface UpdateProjectModalProps {
  open: boolean;
  mode: "edit";
  initialValues?: Partial<UpdateProjectFormValues>;
  onCancel: () => void;
  onSubmit: (data: UpdateProjectFormValues) => void;
}

function UpdateProjectModal({
  open,
  initialValues,
  onCancel,
  onSubmit,
}: UpdateProjectModalProps) {
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<UpdateProjectFormValues>({
    resolver: zodResolver(updateProjectSchema),
    defaultValues: {
      name: initialValues?.name || "",
      description: initialValues?.description || "",
      priority: initialValues?.priority,
      status: initialValues?.status,
      due_date: initialValues?.due_date || "",
    },
  });

  return (
    <Modal
      open={open}
      title={"Update Project"}
      onCancel={onCancel}
      onOk={handleSubmit(onSubmit)}
      okText={"Update"}
      style={{
        top: 20,
      }}
    >
      <div className="space-y-4">
        {/* NAME */}
        <div>
          <label>Name</label>
          <Controller
            control={control}
            name="name"
            render={({ field }) => (
              <Input {...field} placeholder="Enter project name" />
            )}
          />
          {errors.name && (
            <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>
          )}
        </div>

        {/* DESCRIPTION */}
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

        {/* PRIORITY */}
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

        {/* STATUS */}
        <div>
          <label>Status</label>
          <Controller
            control={control}
            name="status"
            render={({ field }) => (
              <Select
                {...field}
                className="w-full"
                allowClear
                options={[
                  { label: "Todo", value: "todo" },
                  { label: "In Progress", value: "in_progress" },
                  { label: "Done", value: "done" },
                ]}
              />
            )}
          />
        </div>

        {/* DUE DATE */}
        <div>
          <label>Due Date</label>
          <Controller
            control={control}
            name="due_date"
            render={({ field }) => (
              <DatePicker
                className="w-full"
                value={field.value ? dayjs(field.value) : null}
                onChange={(date) =>
                  field.onChange(date ? date.format("YYYY-MM-DD") : "")
                }
              />
            )}
          />
          {errors.due_date && (
            <p className="text-red-500 text-sm mt-1">
              {errors.due_date.message}
            </p>
          )}
        </div>
      </div>
    </Modal>
  );
}

export default UpdateProjectModal;
