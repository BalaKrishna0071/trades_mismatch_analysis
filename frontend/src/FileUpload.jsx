import "./FileUpload.css";
import "react-toastify/dist/ReactToastify.css";
import { Bounce, ToastContainer, toast } from "react-toastify";
import React, { useState, useRef } from "react";

function FileUpload() {
  const [files, setFiles] = useState([null, null, null]);
  const [uploaded, setUploaded] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [running, setRunning] = useState(false);
  const [resetting, setResetting] = useState(false);


  // Refs for file inputs for easier reset
  const fileRefs = [useRef(), useRef(), useRef()];

  // Handle file selection
  const handleFileChange = (index, e) => {
    const newFiles = [...files];
    newFiles[index] = e.target.files[0];
    setFiles(newFiles);
  };

  // Upload files
  const handleUpload = async () => {
    if (files.some(file => file === null)) {
      toast.warn("Please select all 3 files before uploading!");
      return;
    }

    setUploading(true);
    const formData = new FormData();
    files.forEach(file => file && formData.append("file", file));

    try {
      const response = await fetch("http://localhost:5007/upload_trades_files", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      console.log("Server Response:", data);

      setUploaded(true);
      toast.success("Files uploaded successfully!");
    } catch (error) {
      console.error("Error uploading files:", error);
      setUploaded(false);
      toast.error("Error uploading files!");
    } finally {
      setUploading(false);
    }
  };

  // Run trade mismatch
  const runTradeMismatch = async () => {
    if (!uploaded) {
      toast.warn("Please upload files first!");
      return;
    }

    setRunning(true);
    toast.info("Started Mismatch Process...");

    try {
      const response = await fetch("http://localhost:5007/run_mismatch", { method: "GET" });
      console.log(response)
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      console.log("Server Response:", data);

      toast.success("Mismatch process completed!");
    } catch (error) {
      console.error("Error running mismatch:", error);
      toast.error("Error in mismatch process!");
    } finally {
      setRunning(false);
    }
  };

  // Reset files and server state
  const handleReset = async () => {
    // Clear file inputs
    fileRefs.forEach(ref => {
      if (ref.current) ref.current.value = "";
    });
    setFiles([null, null, null]);
    setUploaded(false);

    setResetting(true);

    try {
      const response = await fetch("http://localhost:5007/reset_mismatch", { method: "DELETE" });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      console.log("Reset Response:", data);

      toast.success("Reset successful!");
      window.location.reload();
    } catch (error) {
      console.error("Error in resetting process:", error);
      toast.error("Error in resetting process!");
    } finally {
      setResetting(false);
    }
  };

  return (
    <div className="file-upload-wrapper">
      <input ref={fileRefs[0]} type="file" accept=".xls,.xlsx,.xlsm,.csv,.pkl" onChange={(e) => handleFileChange(0, e)} />
      <input ref={fileRefs[1]} type="file" accept=".xls,.xlsx,.xlsm,.csv,.pkl" onChange={(e) => handleFileChange(1, e)} />
      <input ref={fileRefs[2]} type="file" accept=".xls,.xlsx,.xlsm,.csv,.pkl" onChange={(e) => handleFileChange(2, e)} />

      <button onClick={handleUpload} disabled={uploading}>
        {uploading ? "Uploading..." : "Upload"}
      </button>

      <button onClick={runTradeMismatch} disabled={running}>
        {running ? "Running..." : "Run"}
      </button>

      <button className="reset-btn" onClick={handleReset} disabled={running || resetting}>
        {resetting ? "Resetting..." : "Reset"}
      </button>

      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        theme="dark"
        transition={Bounce}
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </div>
  );
}

export default FileUpload;