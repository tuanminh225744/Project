import React, { use, useEffect } from "react";
import { useAuth } from "../contexts/auth_context";
import { useNavigate } from "react-router-dom";

function Dashboard() {
  const [count, setCount] = React.useState(0);
  const { user, login } = useAuth();
  const navigate = useNavigate();
  // updete count when button is clicked
  useEffect(() => {
    console.log("Count has changed:", count);
  }, [count]);

  useEffect(() => {
    console.log("Dashboard component has mounted");
    login();
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      console.log("running");
    }, 1000);

    return () => {
      clearInterval(timer);
      console.log("cleaned");
    };
  }, []);

  const BtnClick = () => {
    navigate("/project");
  };

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Welcome to your dashboard!</p>

      <p>Count: {count}</p>
      <p>User: {user?.name}</p>
      <button onClick={BtnClick}>Sang trang project</button>
    </div>
  );
}

export default Dashboard;
