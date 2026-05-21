import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";

import {
  Button,
  Card,
  Empty,
  Input,
  Select,
  Space,
  Spin,
  Tag,
  Typography,
  message,
} from "antd";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import TaskModal from "../components/task_modal";
import DeleteTaskModal from "../components/delete_task_modal";
import UpdateProjectModal from "../components/update_project_modal";
import DeleteProjectModal from "../components/delete_project_modal";

import {
  createTaskApi,
  deleteTaskApi,
  getTasksByProjectApi,
  updateTaskApi,
  type Task,
  type CreateTaskFormData,
  type UpdateTaskFormData,
} from "../services/task_service";
import {
  updateProjectApi,
  deleteProjectApi,
  getProjectByIdApi,
} from "../services/project_service";
import { getProjectMembersApi } from "../services/project_member_service";
import type {
  CreateProjectFormValues,
  UpdateProjectFormValues,
} from "../schemas/project_schema";

type TaskStatus = "todo" | "in_progress" | "done";

type Priority = "low" | "medium" | "high";

interface MemberItem {
  id: number;
  name: string;
  email: string;
  role: "owner" | "member";
}

const membersMock: MemberItem[] = [
  {
    id: 1,
    name: "Nguyen Van A",
    email: "nguyenvana@example.com",
    role: "owner",
  },

  {
    id: 2,
    name: "Tran Thi B",
    email: "tranthib@example.com",
    role: "member",
  },

  {
    id: 3,
    name: "Le Van C",
    email: "levanc@example.com",
    role: "member",
  },
];

const statusLabels: Record<TaskStatus, string> = {
  todo: "Todo",
  in_progress: "In Progress",
  done: "Done",
};

const statusColors: Record<TaskStatus, string> = {
  todo: "default",
  in_progress: "blue",
  done: "green",
};

const priorityLabels: Record<Priority, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
};

const priorityColors: Record<Priority, string> = {
  low: "green",
  medium: "gold",
  high: "red",
};

const columnHelper = createColumnHelper<Task>();

function ProjectDetail() {
  const navigate = useNavigate();

  const queryClient = useQueryClient();

  const { projectId } = useParams();

  const [searchText, setSearchText] = useState("");

  const [statusFilter, setStatusFilter] = useState<TaskStatus | "all">("all");

  const [priorityFilter, setPriorityFilter] = useState<Priority | "all">("all");

  const [selectedTask, setSelectedTask] = useState<Task | null>(null);

  const [createTaskModalOpen, setCreateTaskModalOpen] = useState(false);

  const [editTaskModalOpen, setEditTaskModalOpen] = useState(false);

  const [deleteTaskModalOpen, setDeleteTaskModalOpen] = useState(false);

  const [updateProjectModalOpen, setUpdateProjectModalOpen] = useState(false);

  const [deleteProjectModalOpen, setDeleteProjectModalOpen] = useState(false);

  const [updateProjectData, setUpdateProjectData] =
    useState<UpdateProjectFormValues | null>(null);

  const { data: tasks = [], isLoading } = useQuery({
    queryKey: ["tasks", projectId],

    queryFn: () => getTasksByProjectApi(Number(projectId)),

    enabled: !!projectId,
  });

  const { data: project } = useQuery({
    queryKey: ["project"],
    queryFn: () => getProjectByIdApi(Number(projectId)),
    enabled: !!projectId,
  });

  const { data: project_members } = useQuery({
    queryKey: ["project_members"],
    queryFn: () => getProjectMembersApi(Number(projectId)),
  });

  const filteredTasks = useMemo(() => {
    const normalizedSearch = searchText.trim().toLowerCase();

    return tasks.filter((task) => {
      const matchesSearch =
        normalizedSearch.length === 0 ||
        task.title.toLowerCase().includes(normalizedSearch) ||
        (task.description || "").toLowerCase().includes(normalizedSearch);

      const matchesStatus =
        statusFilter === "all" || task.status === statusFilter;

      const matchesPriority =
        priorityFilter === "all" || task.priority === priorityFilter;

      return matchesSearch && matchesStatus && matchesPriority;
    });
  }, [tasks, searchText, statusFilter, priorityFilter]);

  const createTaskMutation = useMutation({
    mutationFn: createTaskApi,

    onSuccess: () => {
      message.success("Create task successfully");

      queryClient.invalidateQueries({
        queryKey: ["tasks", projectId],
      });

      setCreateTaskModalOpen(false);
    },

    onError: () => {
      message.error("Create task failed");
    },
  });

  const updateTaskMutation = useMutation({
    mutationFn: ({
      taskId,
      payload,
    }: {
      taskId: number;
      payload: UpdateTaskFormData;
    }) => updateTaskApi(taskId, payload),

    onSuccess: () => {
      message.success("Update task successfully");

      queryClient.invalidateQueries({
        queryKey: ["tasks", projectId],
      });

      setEditTaskModalOpen(false);
      setSelectedTask(null);
    },

    onError: () => {
      message.error("Update task failed");
    },
  });

  const deleteTaskMutation = useMutation({
    mutationFn: deleteTaskApi,

    onSuccess: () => {
      message.success("Delete task successfully");

      queryClient.invalidateQueries({
        queryKey: ["tasks", projectId],
      });

      setDeleteTaskModalOpen(false);
      setSelectedTask(null);
    },

    onError: () => {
      message.error("Delete task failed");
    },
  });

  const updateProjectMutation = useMutation({
    mutationFn: ({
      projectId,
      payload,
    }: {
      projectId: number;
      payload: CreateProjectFormValues;
    }) => updateProjectApi(projectId, payload),
    onSuccess: () => {
      message.success("Update Project successfully");

      queryClient.invalidateQueries({
        queryKey: ["Projects", projectId],
      });
      setUpdateProjectModalOpen(false);
    },
    onError: () => {
      message.error("Update Project failed");
    },
  });

  const deleteProjectMutation = useMutation({
    mutationFn: deleteProjectApi,
    onSuccess: () => {
      message.success("Delete Project successfully");

      queryClient.invalidateQueries({
        queryKey: ["Projects", projectId],
      });
      setDeleteProjectModalOpen(false);
    },
    onError: () => {
      message.error("Delete Project failed");
    },
  });

  const handleCreateTask = (data: CreateTaskFormData) => {
    createTaskMutation.mutate({
      ...data,
      project_id: Number(projectId),
    });
  };

  const handleUpdateTask = (data: UpdateTaskFormData) => {
    if (!selectedTask) return;

    updateTaskMutation.mutate({
      taskId: selectedTask.id,
      payload: data,
    });
  };

  const handleDeleteTask = () => {
    if (!selectedTask) return;

    deleteTaskMutation.mutate(selectedTask.id);
  };

  const handleUpdateProject = (data: UpdateProjectFormValues) => {
    if (!projectId) return;
    setUpdateProjectData(data);
    updateProjectMutation.mutate({
      projectId: Number(projectId),
      payload: data,
    });
  };

  const handleDeleteProject = () => {
    if (!projectId) return;
    deleteProjectMutation.mutate(Number(projectId));
  };

  const columns = useMemo(
    () => [
      columnHelper.accessor("title", {
        header: "Task",

        cell: (info) => {
          const task = info.row.original;

          return (
            <div>
              <Typography.Text strong>{task.title}</Typography.Text>

              <Typography.Paragraph className="!mb-0 !mt-1 text-sm text-slate-500">
                {task.description || "Không có mô tả"}
              </Typography.Paragraph>
            </div>
          );
        },
      }),

      columnHelper.accessor("status", {
        header: "Status",

        cell: (info) => {
          const status = info.getValue();

          return <Tag color={statusColors[status]}>{statusLabels[status]}</Tag>;
        },
      }),

      columnHelper.accessor("priority", {
        header: "Priority",

        cell: (info) => {
          const priority = info.getValue();

          return (
            <Tag color={priorityColors[priority]}>
              {priorityLabels[priority]}
            </Tag>
          );
        },
      }),

      columnHelper.accessor("assignee_id", {
        header: "Assignee ID",

        cell: (info) => info.getValue() || "N/A",
      }),

      columnHelper.accessor("due_date", {
        header: "Due Date",

        cell: (info) => {
          const value = info.getValue();

          return value ? new Date(value).toLocaleDateString("vi-VN") : "N/A";
        },
      }),

      columnHelper.display({
        id: "actions",

        header: "Actions",

        cell: ({ row }) => {
          const task = row.original;

          return (
            <Space>
              <Button
                size="small"
                onClick={() => {
                  setSelectedTask(task);

                  setEditTaskModalOpen(true);
                }}
              >
                Edit
              </Button>

              <Button
                danger
                size="small"
                onClick={() => {
                  setSelectedTask(task);

                  setDeleteTaskModalOpen(true);
                }}
              >
                Delete
              </Button>
            </Space>
          );
        },
      }),
    ],
    [],
  );

  const table = useReactTable({
    data: filteredTasks,

    columns,

    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <main className="min-h-screen bg-slate-100 px-4 py-8">
      <div className="mx-auto w-full max-w-6xl">
        <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <Typography.Text className="text-xs font-semibold uppercase tracking-wide text-blue-600">
              Project #{projectId ? projectId : ""}
            </Typography.Text>

            <Typography.Title level={2} className="!mb-2 !mt-2">
              {project ? project.name : ""}
            </Typography.Title>

            <Typography.Paragraph className="max-w-3xl text-slate-600">
              {project ? project.description : ""}
            </Typography.Paragraph>
          </div>

          <Space wrap>
            <Button onClick={() => navigate("/project")}>Quay lại</Button>

            <Button
              onClick={() => {
                setUpdateProjectModalOpen(true);
              }}
            >
              Sửa project
            </Button>

            <Button danger onClick={() => setDeleteProjectModalOpen(true)}>
              Xóa project
            </Button>

            <Button type="primary" onClick={() => setCreateTaskModalOpen(true)}>
              Tạo task
            </Button>
          </Space>
        </div>

        <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_320px]">
          <Card title="Danh sách task" className="shadow-sm">
            <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <Input.Search
                className="md:max-w-sm"
                placeholder="Tìm task theo tên hoặc mô tả"
                allowClear
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
              />

              <Space wrap>
                <Select
                  className="w-36"
                  value={statusFilter}
                  onChange={setStatusFilter}
                  options={[
                    {
                      value: "all",
                      label: "All Status",
                    },

                    {
                      value: "todo",
                      label: "Todo",
                    },

                    {
                      value: "in_progress",
                      label: "In Progress",
                    },

                    {
                      value: "done",
                      label: "Done",
                    },
                  ]}
                />

                <Select
                  className="w-36"
                  value={priorityFilter}
                  onChange={setPriorityFilter}
                  options={[
                    {
                      value: "all",
                      label: "All Priority",
                    },

                    {
                      value: "low",
                      label: "Low",
                    },

                    {
                      value: "medium",
                      label: "Medium",
                    },

                    {
                      value: "high",
                      label: "High",
                    },
                  ]}
                />
              </Space>
            </div>

            <div className="overflow-x-auto rounded-lg border border-slate-200">
              <table className="min-w-[780px] w-full border-collapse bg-white text-left">
                <thead className="bg-slate-50">
                  {table.getHeaderGroups().map((headerGroup) => (
                    <tr key={headerGroup.id}>
                      {headerGroup.headers.map((header) => (
                        <th
                          key={header.id}
                          className="border-b border-slate-200 px-4 py-3 text-sm font-semibold text-slate-600"
                        >
                          {header.isPlaceholder
                            ? null
                            : flexRender(
                                header.column.columnDef.header,
                                header.getContext(),
                              )}
                        </th>
                      ))}
                    </tr>
                  ))}
                </thead>

                <tbody>
                  {table.getRowModel().rows.map((row) => (
                    <tr key={row.id} className="hover:bg-slate-50">
                      {row.getVisibleCells().map((cell) => (
                        <td
                          key={cell.id}
                          className="border-b border-slate-100 px-4 py-3 align-top"
                        >
                          {flexRender(
                            cell.column.columnDef.cell,
                            cell.getContext(),
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {isLoading ? (
              <div className="flex justify-center py-10">
                <Spin size="large" />
              </div>
            ) : filteredTasks.length === 0 ? (
              <div className="py-10">
                <Empty description="Không tìm thấy task phù hợp" />
              </div>
            ) : null}
          </Card>

          <Card title="Danh sách member" className="shadow-sm">
            <div className="space-y-3">
              {project?.members?.map((member) => (
                <div
                  key={member.id}
                  className="rounded-lg border border-slate-200 bg-white p-3"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <Typography.Text strong>
                        {member.user.username}
                      </Typography.Text>

                      <Typography.Paragraph className="!mb-0 !mt-1 text-sm text-slate-500">
                        {member.user.email}
                      </Typography.Paragraph>
                    </div>

                    <Tag color={member.role === "owner" ? "blue" : "default"}>
                      {member.role}
                    </Tag>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <TaskModal
          open={createTaskModalOpen}
          mode="create"
          onCancel={() => setCreateTaskModalOpen(false)}
          onSubmit={handleCreateTask}
        />

        <TaskModal
          open={editTaskModalOpen}
          mode="edit"
          initialValues={selectedTask || undefined}
          onCancel={() => {
            setEditTaskModalOpen(false);

            setSelectedTask(null);
          }}
          onSubmit={handleUpdateTask}
        />

        <DeleteTaskModal
          open={deleteTaskModalOpen}
          taskTitle={selectedTask?.title}
          onCancel={() => {
            setDeleteTaskModalOpen(false);

            setSelectedTask(null);
          }}
          onConfirm={handleDeleteTask}
        />

        <UpdateProjectModal
          open={updateProjectModalOpen}
          initialValues={updateProjectData}
          mode="edit"
          onCancel={() => {
            setUpdateProjectModalOpen(false);
          }}
          onSubmit={handleUpdateProject}
        />

        <DeleteProjectModal
          open={deleteProjectModalOpen}
          projectName={project.name}
          onCancel={() => {
            setDeleteProjectModalOpen(false);
          }}
          onConfirm={() => {
            handleDeleteProject;
          }}
        />
      </div>
    </main>
  );
}

export default ProjectDetail;
