import React, { useEffect, useState } from "react";
import { Header } from "../Sections/Header";
import { useForm } from "../../context/FormContext";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./smallCSS.css";
import axios from "axios";

export const FileUpload = () => {
  const [fileName] = useState("Choose File");
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
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
    <div>
      <Header
        head="Select File"
        para="Please provide the correct excel file with the queries "
      />
      <main>
        <form
          onSubmit={handleSubmit}
          className="flex flex-col mt-8"
          autoComplete="off"
        >
          <label className="mb-1" htmlFor="projectType">
            Excel file upload
          </label>
          <label className="custom-file-upload">
            <input
              type="file"
              accept=".csv,.xlsx"
              onChange={handleFileChange}
            />
            {fileName}
          </label>
          <button
            className="py-3 float-right mt-[15%] ml-auto hover:bg-blue-900 bg-blue-950 text-sm text-white w-[110px] rounded-lg"
            type="submit"
          >
            Next Step
          </button>
          <ToastContainer />
        </form>
        {message && <p className="message">{message}</p>}
      </main>
    </div>
  );
};
