import React, { useEffect, useState, Component } from "react";
import { Header } from "../Sections/Header";
import { useForm } from "../../context/FormContext";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./smallCSS.css";
import axios from "axios";

export const QueryAns = () => {
  const [showCheckboxes, setShowCheckboxes] = useState(false);
  const [checkboxArray, setCheckboxArray] = useState([]);
  const [checkboxStates, setCheckboxStates] = useState({});
  const [independentCheckbox, setIndependentCheckbox] = useState(false);
  const [showTables, setShowTables] = useState(false);
  const [tableData, setTableData] = useState([]);
  const [activeTableIndex, setActiveTableIndex] = useState(null);
  const [tableCheckboxStates, setTableCheckboxStates] = useState({});
  const [tableDataArray, setTableDataArray] = useState([]);

  // Function to fetch data from backend (replace with actual endpoint)
  const fetchDataFromBackend = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:5000/get_data");
      console.log(response);
      const result = response.data;
      const data = result.data; // Parse the JSON string
      // Check if data is an array
      if (!Array.isArray(data)) {
        throw new Error("Expected an array but got something else");
      }
      // Extract unique suite names
      const uniqueSuiteNames = [
        ...new Set(data.map((item) => item.Suite_Name)),
      ];
      setCheckboxArray(uniqueSuiteNames);
      // Split data into tables by suite_names
      const tablesBySuite = uniqueSuiteNames.map((suite_name) => ({
        suite_name,
        columns: Object.keys(data[0]),
        rows: data.filter((item) => item.Suite_Name === suite_name),
      }));
      setTableDataArray(tablesBySuite);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const handleIndependentCheckboxChange = (checked) => {
    setIndependentCheckbox(checked);
    if (checked) {
      setShowCheckboxes(false);
      setShowTables(false);
      setCheckboxStates({});
      setActiveTableIndex(null);
      fetchDataFromBackend();
    }
  };

  // Handler for first dropdown checkbox
  const handleFirstDropdownChange = (checked) => {
    setShowCheckboxes(checked);
    if (checked) {
      setIndependentCheckbox(false);
      setShowTables(false);
    } else {
      setCheckboxStates({});
    }
  };

  // Handler for third dropdown checkbox
  const handleThirdDropdownChange = (checked) => {
    setShowTables(checked);
    if (checked) {
      setIndependentCheckbox(false);
      setShowCheckboxes(false);
      setCheckboxStates({});
      setActiveTableIndex(null);
    }
  };

  // Handler for checkbox states under second dropdown
  const handleCheckboxChange = (index, checked) => {
    setCheckboxStates((prev) => ({
      ...prev,
      [index]: checked,
    }));
  };

  // Handler for table button click
  const handleTableButtonClick = (index) => {
    if (activeTableIndex === index) {
      setActiveTableIndex(null);
      setTableCheckboxStates((prev) => ({
        ...prev,
        [index]: {},
      }));
    } else {
      setActiveTableIndex(index);
    }
  };

  // Handler for table checkbox states
  const handleTableCheckboxChange = (tableIndex, rowIndex, checked) => {
    setTableCheckboxStates((prev) => ({
      ...prev,
      [tableIndex]: {
        ...prev[tableIndex],
        [rowIndex]: checked,
      },
    }));
  };

  // Function to prepare form data as JSON
  const prepareFormData = () => {
    const formData = {};

    if (independentCheckbox) {
      formData.tables = tableDataArray.map((table) => ({
        item: table.suite_name,
        values: table.rows.map((row) =>
          Array.isArray(row)
            ? row.reduce(
                (acc, cell, index) => ({ ...acc, [`column_${index}`]: cell }),
                {}
              )
            : Object.values(row).reduce(
                (acc, cell, index) => ({ ...acc, [`column_${index}`]: cell }),
                {}
              )
        ),
      }));
    } else {
      formData.tables = tableDataArray
        .map((table, index) => {
          if (checkboxStates[index]) {
            return {
              item: table.suite_name,
              values: table.rows.map((row) =>
                Array.isArray(row)
                  ? row.reduce(
                      (acc, cell, index) => ({
                        ...acc,
                        [`column_${index}`]: cell,
                      }),
                      {}
                    )
                  : Object.values(row).reduce(
                      (acc, cell, index) => ({
                        ...acc,
                        [`column_${index}`]: cell,
                      }),
                      {}
                    )
              ),
            };
          } else if (index === activeTableIndex) {
            return {
              item: table.suite_name,
              values: table.rows
                .filter(
                  (row, rowIndex) => tableCheckboxStates[index]?.[rowIndex]
                )
                .map((row) =>
                  Array.isArray(row)
                    ? row.reduce(
                        (acc, cell, index) => ({
                          ...acc,
                          [`column_${index}`]: cell,
                        }),
                        {}
                      )
                    : Object.values(row).reduce(
                        (acc, cell, index) => ({
                          ...acc,
                          [`column_${index}`]: cell,
                        }),
                        {}
                      )
                ),
            };
          }
          return null;
        })
        .filter((table) => table !== null);
    }

    return formData;
  };

  // Function to submit form data to the backend
  const handleSubmit = async () => {
    const formData = prepareFormData();
    console.log("Form Data:", JSON.stringify(formData, null, 2)); // Log form data for debugging

    try {
      await axios.post("http://127.0.0.1:5000/submit_selection", formData); // Example API endpoint
      alert("Form data submitted successfully!");
    } catch (error) {
      console.error("Error submitting form data:", error);
    }
  };

  // Fetch table data when showTables state changes to true

  useEffect(() => {
    if (showCheckboxes) {
      fetchDataFromBackend();
    }
  }, [showCheckboxes]);

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
      <div className="flex mt-5 mb-5 border-2 rounded-lg border-[#e0def7] w-40 h-10 p-2 transition-all text-center">
        <input
          type="checkbox"
          className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 "
          id="full-exec-box"
          checked={independentCheckbox}
          onChange={(e) => handleIndependentCheckboxChange(e.target.checked)}
        ></input>
        <label htmlFor="full-exec-box" className="ms-2 text-sm font-medium">
          Full Execution
        </label>
      </div>

      {/* First Dropdown */}
      <div className="flex  mb-5 border-2 rounded-lg border-[#e0def7] w-40 h-10 p-2 transition-all text-center">
        <input
          type="checkbox"
          className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 "
          checked={showCheckboxes}
          onChange={(e) => handleFirstDropdownChange(e.target.checked)}
          id="multi-suite-select"
        />
        <label
          htmlFor="multi-suite-select"
          className="ms-2 text-sm font-medium"
        >
          Multi suite select
        </label>
      </div>

      {/* Second Dropdown */}
      {showCheckboxes && (
        <div className="flex flex-col mb-5 border-2 rounded-lg border-[#e0def7] w-64 h-52 overflow-auto p-2 transition-all text-center">
          {checkboxArray.map((item, index) => (
            <div key={index} className="flex m-5">
              <input
                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                type="checkbox"
                checked={checkboxStates[index] || false}
                onChange={(e) => handleCheckboxChange(index, e.target.checked)}
              />
              <label className="ms-2 text-sm font-medium">{item}</label>
            </div>
          ))}
        </div>
      )}

      {/* Third Dropdown */}
      <div className="mb-5 ">
        <label className="border-[#e0def7] border-2 rounded-lg hover:bg-[#e0def7] p-2 text-center ">
          <input
            type="checkbox"
            className="mr-2"
            checked={showTables}
            onChange={(e) => handleThirdDropdownChange(e.target.checked)}
          />
          Multi SQL select
        </label>
        {showTables && (
          <div className="mt-5 h-52 overflow-auto border-2 border-[#e0def7] rounded-lg px-5 pb-5">
            {tableDataArray.map((table, index) => (
              <div key={index} className="mt-5">
                <button
                  className="bg-white border-2 border-[#e0def7] px-4 py-2 rounded-lg"
                  onClick={() => handleTableButtonClick(index)}
                >
                  {table.suite_name}
                </button>
                {activeTableIndex === index && (
                  <table className="mt-4 w-full table-auto">
                    <thead>
                      <tr>
                        {table.columns.map((column, idx) => (
                          <th key={idx} className="border p-2">
                            {column}
                          </th>
                        ))}
                        <th className="border p-2">Select</th>
                      </tr>
                    </thead>
                    <tbody>
                      {table.rows.map((row, rowIndex) => (
                        <tr key={rowIndex}>
                          {Object.values(row).map((cell, cellIndex) => (
                            <td key={cellIndex} className="border p-2">
                              {cell}
                            </td>
                          ))}
                          <td className="border p-2">
                            <input
                              type="checkbox"
                              checked={
                                tableCheckboxStates[index]
                                  ? tableCheckboxStates[index][rowIndex] ||
                                    false
                                  : false
                              }
                              onChange={(e) =>
                                handleTableCheckboxChange(
                                  index,
                                  rowIndex,
                                  e.target.checked
                                )
                              }
                            />
                          </td>
                        </tr>
                      ))}
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
          onClick={handleSubmit}
        >
          Execute
        </button>
      </div>
    </div>
  );
};
