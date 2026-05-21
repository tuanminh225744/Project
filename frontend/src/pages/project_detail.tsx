import { useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { Button, Card, Empty, Input, Select, Space, Tag, Typography } from "antd";

type TaskStatus = "todo" | "inprogress" | "done";
type Priority = "low" | "medium" | "high";

interface TaskItem {
  id: number;
  title: string;
  description: string;
  status: TaskStatus;
  priority: Priority;
  assignee: string;
  dueDate: string;
}

interface MemberItem {
  id: number;
  name: string;
  email: string;
  role: "owner" | "member";
}

const projectMock = {
  name: "Website Redesign",
  description:
    "Thiết kế lại giao diện quản lý project, tối ưu trải nghiệm theo dõi task và tiến độ làm việc của team.",
};

const tasksMock: TaskItem[] = [
  {
    id: 1,
    title: "Thiết kế project detail",
    description: "Dựng layout bảng task và danh sách member.",
    status: "inprogress",
    priority: "high",
    assignee: "Nguyen Van A",
    dueDate: "2026-05-25",
  },
  {
    id: 2,
    title: "Kết nối task API",
    description: "Chuẩn bị service lấy task theo project.",
    status: "todo",
    priority: "medium",
    assignee: "Tran Thi B",
    dueDate: "2026-05-28",
  },
  {
    id: 3,
    title: "Kiểm tra responsive",
    description: "Đảm bảo bảng hiển thị tốt trên màn hình nhỏ.",
    status: "done",
    priority: "low",
    assignee: "Le Van C",
    dueDate: "2026-05-18",
  },
];

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
  inprogress: "In progress",
  done: "Done",
};

const statusColors: Record<TaskStatus, string> = {
  todo: "default",
  inprogress: "blue",
  done: "green",
};

const priorityColors: Record<Priority, string> = {
  low: "green",
  medium: "gold",
  high: "red",
};

const priorityLabels: Record<Priority, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
};

const columnHelper = createColumnHelper<TaskItem>();

function ProjectDetail() {
  const navigate = useNavigate();
  const params = useParams();
  const projectId = params.projectId;
  const [searchText, setSearchText] = useState("");
  const [statusFilter, setStatusFilter] = useState<TaskStatus | "all">("all");
  const [priorityFilter, setPriorityFilter] = useState<Priority | "all">("all");

  const filteredTasks = useMemo(() => {
    const normalizedSearchText = searchText.trim().toLowerCase();

    return tasksMock.filter((task) => {
      const matchesSearch =
        normalizedSearchText.length === 0 ||
        task.title.toLowerCase().includes(normalizedSearchText) ||
        task.description.toLowerCase().includes(normalizedSearchText);
      const matchesStatus = statusFilter === "all" || task.status === statusFilter;
      const matchesPriority = priorityFilter === "all" || task.priority === priorityFilter;

      return matchesSearch && matchesStatus && matchesPriority;
    });
  }, [priorityFilter, searchText, statusFilter]);

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
                {task.description}
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

          return <Tag color={priorityColors[priority]}>{priorityLabels[priority]}</Tag>;
        },
      }),
      columnHelper.accessor("assignee", {
        header: "Assignee",
        cell: (info) => info.getValue(),
      }),
      columnHelper.accessor("dueDate", {
        header: "Due date",
        cell: (info) => new Date(info.getValue()).toLocaleDateString("vi-VN"),
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
              Project #{projectId}
            </Typography.Text>
            <Typography.Title level={2} className="!mb-2 !mt-2">
              {projectMock.name}
            </Typography.Title>
            <Typography.Paragraph className="max-w-3xl text-slate-600">
              {projectMock.description}
            </Typography.Paragraph>
          </div>

          <Space wrap>
            <Button onClick={() => navigate("/project")}>Quay lại</Button>
            <Button>Sửa project</Button>
            <Button danger>Xóa project</Button>
            <Button type="primary">Tạo task</Button>
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
                onChange={(event) => setSearchText(event.target.value)}
              />

              <Space wrap>
                <Select
                  className="w-36"
                  value={statusFilter}
                  onChange={setStatusFilter}
                  options={[
                    { value: "all", label: "All status" },
                    { value: "todo", label: "Todo" },
                    { value: "inprogress", label: "In progress" },
                    { value: "done", label: "Done" },
                  ]}
                />
                <Select
                  className="w-36"
                  value={priorityFilter}
                  onChange={setPriorityFilter}
                  options={[
                    { value: "all", label: "All priority" },
                    { value: "low", label: "Low" },
                    { value: "medium", label: "Medium" },
                    { value: "high", label: "High" },
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
                            : flexRender(header.column.columnDef.header, header.getContext())}
                        </th>
                      ))}
                    </tr>
                  ))}
                </thead>
                <tbody>
                  {table.getRowModel().rows.map((row) => (
                    <tr key={row.id} className="hover:bg-slate-50">
                      {row.getVisibleCells().map((cell) => (
                        <td key={cell.id} className="border-b border-slate-100 px-4 py-3 align-top">
                          {flexRender(cell.column.columnDef.cell, cell.getContext())}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>

              {filteredTasks.length === 0 ? (
                <div className="bg-white py-10">
                  <Empty description="Không tìm thấy task phù hợp" />
                </div>
              ) : null}
            </div>
          </Card>

          <Card title="Danh sách member" className="shadow-sm">
            <div className="space-y-3">
              {membersMock.map((member) => (
                <div
                  key={member.id}
                  className="rounded-lg border border-slate-200 bg-white p-3"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <Typography.Text strong>{member.name}</Typography.Text>
                      <Typography.Paragraph className="!mb-0 !mt-1 text-sm text-slate-500">
                        {member.email}
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
      </div>
    </main>
  );
}

export default ProjectDetail;
