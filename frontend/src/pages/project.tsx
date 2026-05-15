import { useNavigate } from "react-router-dom";
import { Outlet } from "react-router-dom";

function Project() {
  const navigate = useNavigate();
  const btnClick = () => {
    navigate("/project/1");
  };
  return (
    <div>
      <h1>Project</h1>
      <p>List project</p>
      <button onClick={btnClick}>sang trang detal</button>
      <Outlet />
    </div>
  );
}

export default Project;
