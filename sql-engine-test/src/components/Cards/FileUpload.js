import React, { useEffect, useState } from "react";
import { Header } from "../Sections/Header";
import { useForm } from "../../context/FormContext";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./smallCSS.css";
import axios from "axios";

export const FileUpload = () => {
  const [fileName, setFileName] = useState("Choose File");
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [option, setOption] = useState("");
  const [data, setData] = useState([]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setFileName(selectedFile ? selectedFile.name : "Choose File");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setMessage("Please select a file and an option");
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
      setData(JSON.parse(response.data.data));
      toast("smaple warning - Rows inserted: ");
    } catch (error) {
      setMessage("Error uploading file");
      console.error("Error uploading file:", error.response || error.message);
    }
  };

  return (
    <div className="flex-center bg-white rounded p-10 h-fit">
      <div className="font-medium text-3xl mb-2 text-[#0e3374] text-center">
        SQL Execution engine
      </div>
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
            className="py-3 float-right mt-[5%] ml-auto hover:bg-red-500 bg-[#d5292a] text-sm text-white w-[110px] rounded-lg"
            type="submit"
          >
            Upload
          </button>
        </form>
        {message && <p className="message">{message}</p>}
        {data.length > 0 && (
          <div className="flex overflow-auto h-52 border-2 rounded-lg border-[#e0def7]">
            <table>
              <thead>
                <tr>
                  {Object.keys(data[0]).map((key) => (
                    <th key={key}>{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.map((row, index) => (
                  <tr key={index}>
                    {Object.values(row).map((value, i) => (
                      <td key={i}>{value}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
};
