import { useState } from "react";
import { useForm } from "../../context/FormContext";
import { Header } from "../Sections/Header";
import axios from "axios";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import * as XLSX from "xlsx";
import jsPDF from "jspdf";
import "jspdf-autotable";

export const EpicGeneration = () => {
  const [tableData, setTableData] = useState(null);
  const [currentTable, setCurrentTable] = useState(null);
  const [selectedViewError, setSelectedViewError] = useState(false);

  const fetchTableData = async (table) => {
    const response = await fetch(`http://127.0.0.1:5000/${table}`);
    const data = await response.json();
    setTableData(data);
    setCurrentTable(table);
    setSelectedViewError(false);
  };

  const renderTable = () => {
    if (selectedViewError) {
      return (
        <div className="text-red-600 text-center">
          * Select a view dumbass *
        </div>
      );
    }

    if (!tableData) return null;
    return (
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
    );
  };

  const exportToExcel = () => {
    if (!tableData) {
      setSelectedViewError(true);
      return;
    }

    const ws = XLSX.utils.json_to_sheet(tableData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Sheet1");
    XLSX.writeFile(wb, `${currentTable}.xlsx`);
  };

  const exportToPDF = () => {
    if (!tableData) {
      setSelectedViewError(true);
      return;
    }

    const doc = new jsPDF();

    // Add table to PDF
    doc.autoTable({
      head: [Object.keys(tableData[0])],
      body: tableData,
    });

    doc.save(`${currentTable}.pdf`);
  };

  return (
    <div className="bg-white p-10 rounded h-fit flex flex-col">
      <div>
        <div className="font-medium text-3xl mb-2 text-[#0e3374] text-center">
          SQL Execution engine
        </div>
        <Header
          head="Select Report"
          para="Please select the required report view "
        />
        <button
          onClick={() => fetchTableData("table1")}
          className="flex flex-col mt-5 mb-5 border-2 rounded-lg border-[#e0def7] w-40 h-10 p-2 transition-all text-center"
        >
          Summary view
        </button>
        <button
          onClick={() => fetchTableData("table2")}
          className="flex flex-col mb-5 border-2 rounded-lg border-[#e0def7] w-40 h-10 p-2 transition-all text-center"
        >
          Detailed view
        </button>
        <div className="border-2 rounded-lg h-52 w-dvh overflow-auto">
          {renderTable()}
        </div>
      </div>
      {/* Download buttons */}
      <div className="flex justify-end mt-4 space-x-4">
        <button
          onClick={exportToExcel}
          className="border border-gray-400 rounded-md px-4 py-2 bg-blue-500 text-white hover:bg-blue-600"
        >
          Download Excel
        </button>
        <button
          onClick={exportToPDF}
          className="border border-gray-400 rounded-md px-4 py-2 bg-green-500 text-white hover:bg-green-600"
        >
          Download PDF
        </button>
      </div>
    </div>
  );
};
