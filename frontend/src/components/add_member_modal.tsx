import { Modal, Select } from "antd";
import { useState } from "react";
import type { User } from "../services/user_service";

interface Props {
  open: boolean;
  onCancel: () => void;
  onSubmit: (userId: number) => void;
  users: User[];
}

function AddMemberModal({ open, onCancel, onSubmit, users }: Props) {
  const [userId, setUserId] = useState<number | null>(null);

  return (
    <Modal
      open={open}
      title="Add member"
      onCancel={onCancel}
      onOk={() => userId && onSubmit(userId)}
    >
      <Select
        className="w-full"
        placeholder="Select user"
        onChange={(value) => setUserId(value)}
        options={users.map((u) => ({
          label: u.username,
          value: u.id,
        }))}
      />
    </Modal>
  );
}

export default AddMemberModal;
