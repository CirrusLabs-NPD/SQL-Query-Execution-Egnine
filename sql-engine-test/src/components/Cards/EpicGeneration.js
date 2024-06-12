import { useState } from "react";
import { useForm } from "../../context/FormContext";
import { Header } from "../Sections/Header";
import axios from "axios";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

export const EpicGeneration = () => {
  const [tableData, setTableData] = useState(null);
  const [currentTable, setCurrentTable] = useState(null);

  const fetchTableData = async (table) => {
    const response = await fetch(`http://127.0.0.1:5000/${table}`);
    const data = await response.json();
    setTableData(data);
    setCurrentTable(table);
  };

  const renderTable = () => {
    if (!tableData) return null;
    return (
      <table>
        <tbody>
          {tableData.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {row.map((cell, cellIndex) => (
                <td key={cellIndex}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  return (
    <div className="bg-white p-10 rounded h-fit flex flex-col">
      <div>
        <button
          onClick={() => fetchTableData("table1")}
          className="flex flex-col mb-5 border-2 rounded-lg border-[#e0def7] w-40 h-10 p-2 transition-all text-center"
        >
          Summary view
        </button>
        <button
          onClick={() => fetchTableData("table2")}
          className="flex flex-col mb-5 border-2 rounded-lg border-[#e0def7] w-40 h-10 p-2 transition-all text-center"
        >
          Detailed view
        </button>
        <div>
          {currentTable && (
            <h2>Showing {currentTable.replace("table", "Table ")}</h2>
          )}
          {renderTable()}
        </div>
      </div>
    </div>
  );
};
