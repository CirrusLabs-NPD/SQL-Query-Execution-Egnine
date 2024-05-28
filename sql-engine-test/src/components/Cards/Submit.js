

import thankIcon from "../../assets/icon-thank-you.svg";
import { useForm } from "../../context/FormContext";

export const Submit = () => {
  const { addInfo , data } = useForm();
  function handleBack(e) {
    e.preventDefault();

    const newData = {
      name: "",
      projectId: "",
      ans01:"",
      ans02:"",
      ans03:"",
      ans04:"",
      accumulatedResponse: "",
      display: 0,
    };
    addInfo(newData);
  }

  const parentKey = data.parentKey;
  console.log(parentKey)
  function openJiraEpic() {
    // Call the AP.jira.openIssueDialog with appropriate parameters
    // eslint-disable-next-line no-undef
    AP.jira.openIssueDialog(`${parentKey}`, function () {
      // Callback function if needed
    });
  }

  return (
    <div className="w-[100%] h-[100%]">
        <main className="flex item-center justify-center h-[100%]">
            <div className="text-center">
                <div>
                    <img className="inline" src={thankIcon} alt="thank-Icon" />
                </div>
                <h2 className="mt-[5%] text-3xl font-bold">Thank you!</h2>
                <p className="mt-[5%] text-center text-slate-400">We hope you have fun using our platform. If you ever need support, please feel free to email us at info@cirruslabs.io</p>
                <p className="mt-4 text-center text-sm text-blue-900">
                Click <span className="underline cursor-pointer" onClick={openJiraEpic}>here</span> to open created epic in jira.
              </p>
              <button
              onClick={handleBack}
              className=" py-3 hover:bg-blue-950 bg-blue-900 text-sm text-white w-[110px] rounded-lg mt-80 ml-4 " // Adjust margin-left here for positioning
            >
              Start Over
            </button>
                </div>
            <div className="mt-[9%]">
            
            </div>
            
        </main>
        
    </div>
    
  )
}
 