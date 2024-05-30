import {
  FileUpload,
  QueryAns,
  EpicGeneration,
  UserStoryGen,
} from "./components";
import { useForm } from "./context/FormContext";
import "./App.css";
import logo from "./logo.png";

function App() {
  const { data } = useForm();
  const today = new Date();
  const month = today.getMonth() + 1;
  const day = today.getDate();
  const year = today.getFullYear();
  const currentDate = day + "/" + month + "/" + year;

  const renderLogo = () => (
    <div>
      <div className="flex items-center">
        <img
          className="logo-icon"
          style={{
            height: "56%",
            width: "30%",
            backgroundColor: "white",
            borderRadius: "12px",
          }}
          src={logo}
          alt="Your Logo"
        />

        <div className="public-layout-logo-text ml-2 text-white">
          <div className="public-layout-logo-prefix">
            <b style={{ fontWeight: "600" }}>SQL </b> Execution Engine
          </div>
          <div className="public-layout-logo-suffix"></div>
        </div>
      </div>
    </div>
  );

  return (
    <section className="bg-white p-5 flex rounded-[2.5%]">
      <div className="bg-[url(./assets/bg-sidebar-desktop.svg)] px-8 py-10 w-[28%] bg-no-repeat bg-contain">
        <div className="flex gap-3 mb-8">{renderLogo()}</div>

        <div className="flex gap-3 mb-8">
          <div
            className={`rounded-full ${
              data.display === 0 ? "bg-sky-200 text-slate-900" : ""
            } text-sky-200 hover:text-slate-900 border-2 border-sky-200 flex items-center justify-center hover:bg-sky-200 w-[35px] h-[35px]`}
          >
            <span>1</span>
          </div>
          <div className="flex flex-col">
            <span className="text-slate-200 text-xs">STEP 1</span>
            <span className="font-medium text-sm text-slate-50">
              SQL Upload
            </span>
          </div>
        </div>
        <div className="flex gap-3 mb-8">
          <div
            className={`rounded-full ${
              data.display === 1 ? "bg-sky-200 text-slate-900" : ""
            } text-sky-200 hover:text-slate-900 border-2 border-sky-200 flex items-center justify-center hover:bg-sky-200 w-[35px] h-[35px]`}
          >
            <span>2</span>
          </div>
          <div className="flex flex-col">
            <span className="text-slate-200 text-xs">STEP 2</span>
            <span className="font-medium text-sm text-slate-50">
              SQL Execution
            </span>
          </div>
        </div>
        <div className="flex gap-3 mb-8">
          <div
            className={`rounded-full ${
              data.display === 2 ? "bg-sky-200 text-slate-900" : ""
            } text-sky-200 hover:text-slate-900 border-2 border-sky-200 flex items-center justify-center hover:bg-sky-200 w-[35px] h-[35px]`}
          >
            <span>3</span>
          </div>
          <div className="flex flex-col">
            <span className="text-slate-200 text-xs">STEP 3</span>
            <span className="font-medium text-sm text-slate-50">
              Report View
            </span>
          </div>
        </div>
      </div>

      <div className="pl-[13%] pr-[4%] pt-[5%] w-[68%]">
        {data.display === 0 ? (
          <FileUpload />
        ) : data.display === 1 ? (
          <QueryAns />
        ) : data.display === 2 ? (
          <EpicGeneration />
        ) : data.display === 3 ? (
          <UserStoryGen />
        ) : (
          ""
        )}
      </div>
    </section>
  );
}

export default App;
