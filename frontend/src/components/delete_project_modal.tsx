import { Modal, Typography } from "antd";

interface DeleteProjectModalProps {
  open: boolean;
  projectName?: string;
  onCancel: () => void;
  onConfirm: () => void;
}

function DeleteProjectModal({
  open,
  projectName,
  onCancel,
  onConfirm,
}: DeleteProjectModalProps) {
  return (
    <Modal
      open={open}
      title="Delete Project"
      onCancel={onCancel}
      onOk={onConfirm}
      okButtonProps={{ danger: true }}
      okText="Delete"
    >
      <Typography.Text>Are you sure you want to delete:</Typography.Text>

      <Typography.Paragraph strong className="!mt-2">
        {projectName}
      </Typography.Paragraph>
    </Modal>
  );
}

export default DeleteProjectModal;
