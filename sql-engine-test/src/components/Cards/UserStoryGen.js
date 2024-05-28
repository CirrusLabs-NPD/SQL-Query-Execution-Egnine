import React, { useState } from 'react';
import { useForm } from "../../context/FormContext";
import { Header } from "../Sections/Header";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Loader from "../Shared/Loader/Loader";

export const UserStoryGen = () => {
  const { data, addInfo, goBack } = useForm();
  const [loading, setLoading] = useState(false); 
  console.log(data.storyResponse.userStories)
  const url = process.env.REACT_APP_URL;

  function handleBack(e) {
    e.preventDefault();
    let data = {
      display: 2,
    };
    goBack(data);
  }

  const handleSubmit = async (e) => {
    e.preventDefault();

    const name = data.name;
    const projectId = data.projectId;
    const parentKey = data.parentKey;

    try {

      setLoading(true);


        const response = await fetch(`${url}getIssueType?jiraBaseUrl=${name}&projectId=${projectId}&issueName=story`);
        const resData = await response.json();

        // Assuming the API always returns an array with one object
        if (resData.length > 0) {
            const issueId = resData[0].id;
            console.log(issueId); // Check if issueId is correctly set
            const payload = {
                jiraBaseUrl: name,
                storyList: {
                    issueUpdates: data.storyResponse.userStories.map((userStory) => ({
                        fields: {
                            project: { id: projectId },
                            parent: { key: parentKey },
                            summary: userStory.title,
                            description: `${userStory.description}\n\nAcceptance Criteria:\n${userStory.acceptanceCriteria}`,
                            issuetype: { id: issueId }
                        }
                    }))
                }
            };

            console.log(payload);

            fetch(`${url}createStories`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Response:', data);
                    toast.success('Stories Added Successful!');
                    let additionalData = {
                        display: 4,
                    };
                    addInfo(additionalData);
                })
                
                .catch(error => {
                    // Handle errors
                    console.error('Error:', error);
                    // Show error message
                    toast.error('API call failed. Please try again later.');
                })
                .finally(() => {
                  setLoading(false); // Set loading to false when API call finishes (whether success or error)
                });
        }
    } catch (error) {
        console.error('Error fetching issue type:', error);
        // Handle error accordingly
    }
};

  return (
    <div>
      <ToastContainer />
      <Header
        head="Generate User Story"
        para="Generating user stories based on epic."
      />
      <main>
      {loading && <Loader />} 
        <form
          onSubmit={handleSubmit}
          className="flex flex-col mt-8"
          autocomplete="off"
        >
          <div
            className="bg-slate-50 p-5"
            style={{ height: "500px", overflowY: "scroll" }}
          >
            <div className="pb-5 border-b-[1px]">
              <div>
                {data.storyResponse.userStories.map((story, index) => (
                  <div key={index} className="card">
                    <h6>
                      <strong>
                        {index + 1} {" ."} {story.title}
                      </strong>
                    </h6>
                    <p>{story.description}</p>
                    <p>
                      <strong>Acceptance Criteria:</strong>
                    </p>
                    <ul>
                    <ul>
                    {story.acceptanceCriteria && (
                      <li>{story.acceptanceCriteria}</li>
                    )}
                  </ul>
                  
                  </ul>                  
                    <div style={{ marginBottom: "30px" }}></div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-[9%]">
            <button
              onClick={handleBack}
              className="text-slate-400 hover:text-blue-900"
            >
              Go Back
            </button>
            <button
              type="submit"
              className="py-3 float-right ml-auto hover:bg-blue-950 bg-blue-900 text-sm text-white w-[110px] rounded-lg"
            >
              Add to Jira
            </button>
          </div>
        </form>
      </main>
    </div>
  );
};
