import React, { useEffect, useState, Component } from "react";
import { Header } from "../Sections/Header";
import { useForm } from "../../context/FormContext";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./smallCSS.css";
import {
  Button,
  Radio,
  RadioGroup,
  FormControlLabel,
  Checkbox,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from "@material-ui/core";
import MaterialTable from "material-table";
import axios from "axios";

export const QueryAns = () => {
  const [showCheckboxes, setShowCheckboxes] = useState(false);
  const [checkboxArray, setCheckboxArray] = useState([
    // dummy array to be changed so that backend array can be fed
    "Department validation",
    "Employee validation",
    "customer validation",
    "Thingamagigy validation",
    "one more validation",
  ]);

  const [showTables, setShowTables] = useState(false);
  const [tableData, setTableData] = useState([]);

  // Function to fetch data from backend (replace with actual endpoint)
  const fetchDataFromBackend = async () => {
    try {
      const response = await axios.get(
        "https://jsonplaceholder.typicode.com/posts"
      ); // Example API
      setTableData(response.data.slice(0, 4)); // Limiting to 4 for example purposes
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  // Fetch table data when showTables state changes to true
  useEffect(() => {
    if (showTables) {
      fetchDataFromBackend();
    }
  }, [showTables]);

  return (
    <div className="bg-white p-10 rounded h-fit flex flex-col">
      <div className="font-medium text-3xl mb-2 text-[#0e3374] text-center">
        SQL Execution engine
      </div>
      <Header
        head="Direct Execution"
        para="Please provide the correct execution for the SQL queries "
      />
      <div className="flex mt-10 mb-5 border-2 rounded-lg border-[#e0def7] w-40 h-10 p-2 transition-all text-center">
        <input
          type="checkbox"
          className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 "
          id="full-exec-box"
        ></input>
        <label for="full-exec-box" className="ms-2 text-sm font-medium">
          Full Execution
        </label>
      </div>

      {/* First Dropdown */}
      <div className="flex  mb-5 border-2 rounded-lg border-[#e0def7] w-40 h-10 p-2 transition-all text-center">
        <input
          type="checkbox"
          className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 "
          onChange={(e) => setShowCheckboxes(e.target.checked)}
          id="multi-suite-select"
        />
        <label for="multi-suite-select" className="ms-2 text-sm font-medium">
          Multi suite select
        </label>
      </div>

      {/* Second Dropdown */}
      {showCheckboxes && (
        <div className="flex flex-col mb-5 border-2 rounded-lg border-[#e0def7] w-64 h-fit p-2 transition-all text-center">
          <h3 className="bg-[#e0def7] rounded-lg p-1">Suite List</h3>
          {checkboxArray.map((item, index) => (
            <div key={index} className="flex m-5 ">
              <input
                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 "
                type="checkbox"
              />
              <label className="ms-2 text-sm font-medium">{item}</label>
            </div>
          ))}
        </div>
      )}

      {/* Third Dropdown */}
      <div className="mb-5 ">
        <button
          className="border-[#e0def7] border-2 rounded-lg hover:bg-[#e0def7] p-5 text-center "
          onClick={() => setShowTables(!showTables)}
        >
          {showTables ? "Close Multi SQL select" : "Show Multi SQL select"}
        </button>
        {showTables && (
          <div className="m-5 h-52 overflow-auto">
            {checkboxArray.map((item, index) => (
              <div key={index} className="mt-5">
                <label>{item}</label>
                {tableData[index] && (
                  <table border="1" style={{ marginTop: "10px" }}>
                    <thead>
                      <tr>
                        {Object.keys(tableData[index]).map((key) => (
                          <th key={key}>{key}</th>
                        ))}
                        <th>Select</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        {Object.values(tableData[index]).map(
                          (value, valueIndex) => (
                            <td key={valueIndex}>{value}</td>
                          )
                        )}
                        <td>
                          <input type="checkbox" />
                        </td>
                      </tr>
                    </tbody>
                  </table>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
      <div>
        <button
          className="py-3 float-right mt-[5%] ml-auto hover:bg-red-500 bg-[#d5292a] text-sm text-white w-[110px] rounded-lg"
          type="submit"
        >
          Execute
        </button>
      </div>
    </div>
  );
};
