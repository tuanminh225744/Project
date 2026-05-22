import { Modal, Typography } from "antd";

interface DeleteTaskModalProps {
  open: boolean;
  taskTitle?: string;
  onCancel: () => void;
  onConfirm: () => void;
}

function DeleteTaskModal({
  open,
  taskTitle,
  onCancel,
  onConfirm,
}: DeleteTaskModalProps) {
  return (
    <Modal
      open={open}
      title="Delete Task"
      onCancel={onCancel}
      onOk={onConfirm}
      okButtonProps={{ danger: true }}
      okText="Delete"
    >
      <Typography.Text>Are you sure you want to delete:</Typography.Text>

      <Typography.Paragraph strong className="!mt-2">
        {taskTitle}
      </Typography.Paragraph>
    </Modal>
  );
}

export default DeleteTaskModal;
