import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Alert,
  Button,
  Card,
  Empty,
  Form,
  Input,
  Modal,
  Select,
  Spin,
  Typography,
} from "antd";
import { Controller, useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import {
  createProjectSchema,
  type CreateProjectFormValues,
} from "../schemas/project_schema";
import {
  createProjectApi,
  getProjectsApi,
  type CreateProjectPayload,
  type Project as ProjectItem,
} from "../services/project_service";

function Project() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CreateProjectFormValues>({
    resolver: zodResolver(createProjectSchema),
    defaultValues: {
      name: "",
      description: "",
      priority: "medium",
      due_date: "",
    },
  });
  const [isModalOpen, setIsModalOpen] = useState(false);

  const projectsQuery = useQuery({
    queryKey: ["projects"],
    queryFn: getProjectsApi,
  });

  const createProjectMutation = useMutation({
    mutationFn: createProjectApi,
    onMutate: async (newProject: CreateProjectPayload) => {
      await queryClient.cancelQueries({ queryKey: ["projects"] });

      const previousProjects = queryClient.getQueryData<ProjectItem[]>([
        "projects",
      ]);
      const optimisticProject: ProjectItem = {
        id: Date.now() * -1,
        name: newProject.name,
        description: newProject.description || null,
        priority: newProject.priority,
        due_date: newProject.due_date,
        owner_id: 0,
        created_at: new Date().toISOString(),
        updated_at: null,
        members: null,
      };

      queryClient.setQueryData<ProjectItem[]>(
        ["projects"],
        (currentProjects = []) => [optimisticProject, ...currentProjects],
      );

      return { previousProjects };
    },
    onError: (_error, _newProject, context) => {
      queryClient.setQueryData(["projects"], context?.previousProjects);
    },
    onSuccess: (createdProject) => {
      queryClient.setQueryData<ProjectItem[]>(
        ["projects"],
        (currentProjects = []) => [
          createdProject,
          ...currentProjects.filter((project) => project.id > 0),
        ],
      );
      setIsModalOpen(false);
      reset();
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });

  const projects = projectsQuery.data ?? [];

  const handleOpenCreateModal = () => {
    reset();
    setIsModalOpen(true);
  };

  const handleCreateProject = (values: CreateProjectFormValues) => {
    createProjectMutation.mutate({
      name: values.name,
      description: values.description,
      priority: values.priority,
      due_date: `${values.due_date}T00:00:00`,
    });
  };

  const errorMessage =
    projectsQuery.isError || createProjectMutation.isError
      ? "Có lỗi xảy ra. Vui lòng thử lại."
      : "";

  return (
    <main className="min-h-screen bg-slate-100 px-4 py-8">
      <div className="mx-auto w-full max-w-5xl">
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <Typography.Text className="text-xs font-semibold uppercase tracking-wide text-blue-600">
              Project Management
            </Typography.Text>
            <Typography.Title level={2} className="!mb-0 !mt-2">
              Danh sách project
            </Typography.Title>
          </div>

          <Button
            type="primary"
            size="large"
            onClick={handleOpenCreateModal}
            disabled={createProjectMutation.isPending}
          >
            Tạo project
          </Button>
        </div>

        {errorMessage ? (
          <Alert
            className="mb-4"
            type="error"
            message={errorMessage}
            action={
              projectsQuery.isError ? (
                <Button size="small" onClick={() => projectsQuery.refetch()}>
                  Tải lại
                </Button>
              ) : null
            }
            showIcon
          />
        ) : null}

        {projectsQuery.isLoading ? (
          <div className="flex min-h-64 items-center justify-center">
            <Spin size="large" />
          </div>
        ) : projects.length === 0 ? (
          <Card>
            <Empty description="Chưa có project nào">
              <Button type="primary" onClick={handleOpenCreateModal}>
                Tạo project đầu tiên
              </Button>
            </Empty>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {projects.map((project) => (
              <Card
                key={project.id}
                className="shadow-sm"
                hoverable
                onClick={() => {
                  if (project.id > 0) {
                    navigate(`/project/${project.id}`);
                  }
                }}
              >
                <div className="flex h-full flex-col gap-3">
                  <div>
                    <Typography.Title level={4} className="!mb-1">
                      {project.name}
                    </Typography.Title>
                    <Typography.Paragraph className="!mb-0 text-slate-600">
                      {project.description || "Không có mô tả"}
                    </Typography.Paragraph>
                  </div>

                  <Typography.Text className="mt-auto text-sm text-slate-500">
                    {project.id < 0
                      ? "Đang tạo..."
                      : `Tạo ngày ${new Date(project.created_at).toLocaleDateString("vi-VN")}`}
                  </Typography.Text>
                </div>
              </Card>
            ))}
          </div>
        )}

        <Modal
          title="Tạo project"
          open={isModalOpen}
          okText="Tạo"
          cancelText="Hủy"
          confirmLoading={createProjectMutation.isPending}
          onCancel={() => setIsModalOpen(false)}
          onOk={handleSubmit(handleCreateProject)}
          destroyOnHidden
        >
          <Form
            layout="vertical"
            requiredMark={false}
            onSubmitCapture={handleSubmit(handleCreateProject)}
          >
            <Form.Item
              label="Tên project"
              validateStatus={errors.name ? "error" : undefined}
              help={errors.name?.message}
            >
              <Controller
                name="name"
                control={control}
                render={({ field }) => (
                  <Input {...field} placeholder="Nhập tên project" />
                )}
              />
            </Form.Item>

            <Form.Item
              label="Priority"
              validateStatus={errors.priority ? "error" : undefined}
              help={errors.priority?.message}
            >
              <Controller
                name="priority"
                control={control}
                render={({ field }) => (
                  <Select
                    {...field}
                    options={[
                      { value: "low", label: "Low" },
                      { value: "medium", label: "Medium" },
                      { value: "high", label: "High" },
                    ]}
                  />
                )}
              />
            </Form.Item>

            <Form.Item
              label="Due date"
              validateStatus={errors.due_date ? "error" : undefined}
              help={errors.due_date?.message}
            >
              <Controller
                name="due_date"
                control={control}
                render={({ field }) => <Input {...field} type="date" />}
              />
            </Form.Item>

            <Form.Item label="Mô tả">
              <Controller
                name="description"
                control={control}
                render={({ field }) => (
                  <Input.TextArea
                    {...field}
                    rows={4}
                    placeholder="Nhập mô tả project"
                  />
                )}
              />
            </Form.Item>
          </Form>
        </Modal>
      </div>
    </main>
  );
}

export default Project;
