import {
  FileUpload,
  QueryAns,
  EpicGeneration,
  UserStoryGen,
} from "./components";
import React, { useEffect, useState } from "react";
import { useForm } from "./context/FormContext";
import "./App.css";
import logo from "./logo.png";
import MaterialTable from "material-table";

function App() {
  const [username, setUsername] = useState("test-username: Raghav");
  const { data, updateDisplay } = useForm();
  const today = new Date();
  const months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];
  const m = today.getMonth();
  let month = months[m];
  const date = today.getDate();
  const days = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ];
  let day = days[today.getDay()];
  const year = today.getFullYear();
  const hour = today.getHours();
  const minute = today.getMinutes();
  const currentDate =
    day +
    ", " +
    month +
    " " +
    date +
    ", " +
    year +
    "      " +
    hour +
    ":" +
    minute;

  const handleClickToPage1 = () => {
    updateDisplay(0);
  };

  const handleClickToPage2 = () => {
    updateDisplay(1);
  };

  const handleClickToPage3 = () => {
    updateDisplay(2);
  };

  return (
    <div className="font-sans">
      <div className="flex flex-row basis-full bg-[#f9f9f9] h-14 p-2 items-center justify-between">
        <img className="px-10" src={logo}></img>
        <div className="flex flex-rows gap-5 mb-1 whitespace-pre ps-32">
          {currentDate}
        </div>
        <div className="flex self-center px-10 ">{username}</div>
      </div>
      <section className="flex">
        <div className="bg-white w-64 p-5 pt-14">
          <div className="flex gap-1 mb-1">
            <div
              onClick={handleClickToPage1}
              className={`flex flex-col ${
                data.display === 0 ? "bg-neutral-200 text-[#0e3374]" : ""
              } hover:bg-neutral-200 hover:text-[#0e3374] flex p-2 justify-center w-full h-[35px] rounded cursor-pointer`}
            >
              <span className="font-medium text-sm">SQL Upload</span>
            </div>
          </div>
          <div className="flex gap-1 mb-1">
            <div
              onClick={handleClickToPage2}
              className={`flex flex-col ${
                data.display === 1 ? "bg-neutral-200 text-[#0e3374]" : ""
              } hover:bg-neutral-200 hover:text-[#0e3374] flex p-2 justify-center w-full h-[35px] rounded cursor-pointer`}
            >
              <span className="font-medium text-sm">SQL Execution</span>
            </div>
          </div>
          <div className="flex gap-1 mb-1">
            <div
              onClick={handleClickToPage3}
              className={`flex flex-col ${
                data.display === 2 ? "bg-neutral-200 text-[#0e3374]" : ""
              } hover:bg-neutral-200 hover:text-[#0e3374] flex p-2 justify-center w-full h-[35px] rounded cursor-pointer`}
            >
              <span className="font-medium text-sm">Report</span>
            </div>
          </div>
        </div>

        <div className="pl-[13%] pr-[4%] pt-[5%] w-[68%]">
          {data.display === 0 ? (
            <FileUpload></FileUpload>
          ) : data.display === 1 ? (
            <QueryAns />
          ) : data.display === 2 ? (
            <EpicGeneration />
          ) : (
            ""
          )}
        </div>
      </section>
    </div>
  );
}

export default App;
