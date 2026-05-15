import { useParams } from "react-router-dom";
function ProjectDetail() {
  const params = useParams();
  const ProjectId = params.projectId;
  return (
    <div>
      <h1>ProjectDetail</h1>
      <p>List projectDetail {ProjectId}</p>
    </div>
  );
}

export default ProjectDetail;
