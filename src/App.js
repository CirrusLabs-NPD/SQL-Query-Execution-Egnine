import React, { useState } from 'react';
import logo from "./cllogo.png";
import "./App.css";

function App() {
  const [status, setStatus] = useState('Status:');
  const [executionType, setExecutionType] = useState('');
  const [empValidation, setEmpValidation] = useState(false);
  const [depValidation, setDepValidation] = useState(false);
  const [empQry1, setEmpQry1] = useState(false);
  const [empQry2, setEmpQry2] = useState(false);
  const [depQry1, setDepQry1] = useState(false);
  const [depQry2, setDepQry2] = useState(false);

  const handleExecution = () => {
    // For demonstration purposes, randomly choose between success and failure
    if (Math.random() > 0.5) {
      setStatus('Status: Executed Successfully');
    } else {
      setStatus('Status: Failed to Upload Excel File');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-4xl bg-white p-10 rounded-lg shadow-lg">
        <header className="flex items-center border-b pb-5 mb-5">

          <div className="flex-shrink-0">
            <img src={logo} alt="Logo" className="h-12 w-12" />
          </div>

          <div className="flex-grow text-center">
            <h1 className="text-2xl font-bold text-gray-800">SQL Query Execution</h1>
            <div className="flex justify-between text-gray-600">
              <span>User: xxx</span>
              <span>Date: {new Date().toLocaleDateString()}</span>
            </div>
          </div>
        </header>


        <main className='flex flex-col justify-center'>
          <h2 className=" text-xl font-bold text-gray-800 mb-5 text-center">SQL Execution</h2>
          <div className="space-y-4">
            <div>
              <input
                type="radio"
                id="fullExecution"
                name="execution"
                value="fullExecution"
                checked={executionType === 'fullExecution'}
                onChange={(e) => setExecutionType(e.target.value)}
                className="mr-2"
              />
              <label htmlFor="fullExecution" className="text-gray-800">Full Execution</label>
            </div>
            <div>
              <input
                type="radio"
                id="multiSuiteSelect"
                name="execution"
                value="multiSuiteSelect"
                checked={executionType === 'multiSuiteSelect'}
                onChange={(e) => setExecutionType(e.target.value)}
                className="mr-2"
              />
              <label htmlFor="multiSuiteSelect" className="text-gray-800">Multi Suite Select</label>
              {executionType === 'multiSuiteSelect' && (
                <div className="ml-6 space-y-2">
                  <div>
                    <input
                      type="checkbox"
                      id="empValidationSuite"
                      checked={empValidation}
                      onChange={(e) => setEmpValidation(e.target.checked)}
                      className="mr-2"
                    />
                    <label htmlFor="empValidationSuite" className="text-gray-800">Emp. Validation</label>
                  </div>
                  <div>
                    <input
                      type="checkbox"
                      id="depValidationSuite"
                      checked={depValidation}
                      onChange={(e) => setDepValidation(e.target.checked)}
                      className="mr-2"
                    />
                    <label htmlFor="depValidationSuite" className="text-gray-800">Dep. Validation</label>
                  </div>
                </div>
              )}
            </div>
            <div>
              <input
                type="radio"
                id="multiSQLSelect"
                name="execution"
                value="multiSQLSelect"
                checked={executionType === 'multiSQLSelect'}
                onChange={(e) => setExecutionType(e.target.value)}
                className="mr-2"
              />
              <label htmlFor="multiSQLSelect" className="text-gray-800">Multi SQL Select</label>
              {executionType === 'multiSQLSelect' && (
                <div className="ml-6 space-y-2">
                  <div>
                    <label className="text-gray-800">Emp. Validation</label>
                    <div className="ml-4 space-y-1">
                      <div>
                        <input
                          type="checkbox"
                          id="empQry1"
                          checked={empQry1}
                          onChange={(e) => setEmpQry1(e.target.checked)}
                          className="mr-2"
                        />
                        <label htmlFor="empQry1" className="text-gray-800">Qry 1</label>
                      </div>
                      <div>
                        <input
                          type="checkbox"
                          id="empQry2"
                          checked={empQry2}
                          onChange={(e) => setEmpQry2(e.target.checked)}
                          className="mr-2"
                        />
                        <label htmlFor="empQry2" className="text-gray-800">Qry 2</label>
                      </div>
                    </div>
                  </div>
                  <div>
                    <label className="text-gray-800">Dep. Validation</label>
                    <div className="ml-4 space-y-1">
                      <div>
                        <input
                          type="checkbox"
                          id="depQry1"
                          checked={depQry1}
                          onChange={(e) => setDepQry1(e.target.checked)}
                          className="mr-2"
                        />
                        <label htmlFor="depQry1" className="text-gray-800">Qry 1</label>
                      </div>
                      <div>
                        <input
                          type="checkbox"
                          id="depQry2"
                          checked={depQry2}
                          onChange={(e) => setDepQry2(e.target.checked)}
                          className="mr-2"
                        />
                        <label htmlFor="depQry2" className="text-gray-800">Qry 2</label>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            <button
              onClick={handleExecution}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Execute
            </button>
            <p className="text-gray-800 font-bold mt-4">{status}</p>
          </div>
        </main>

      </div>
    </div>
  );
}

export default App;
