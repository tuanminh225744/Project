import { useSearchParams } from "react-router-dom";
import { useLocation } from "react-router-dom";

export default function User() {
  let [searchParams] = useSearchParams();
  const location = useLocation();
  const page = searchParams.get("page");
  const limit = searchParams.get("limit");
  return (
    <>
      <p>page: {page}</p>
      <p>limit: {limit}</p>
      <p>pathname: {location.pathname}</p>
      <p>search: {location.search}</p>
    </>
  );
}
