import React, { useState } from "react";
import axios from "axios";
import "./App.css";

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setMessage("Please select a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/upload", // make sure to change the url to .env
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      setMessage("File uploaded successfully");
    } catch (error) {
      setMessage("Error uploading file");
      console.error(error);
    }
  };

  return (
    <div className="file-upload-container">
      <h2>Upload File</h2>
      <form onSubmit={handleSubmit}>
        <input type="file" accept=".csv,.xlsx" onChange={handleFileChange} />
        <button type="submit">Upload</button>
      </form>
      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default FileUpload;
