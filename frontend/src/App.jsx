import React from "react";
import DataTable from "./DataTable";
import FileUpload from "./FileUpload";
import "./DataTable.css";

function App() {
  return (
    <div className="app-wrapper">
      <h1 className="main-title">Trade Mismatch Analysis</h1>
      <FileUpload />
      <DataTable />
    </div>
  );
}

export default App;