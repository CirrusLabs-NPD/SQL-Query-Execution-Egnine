import React, { useEffect, useState } from 'react';
import { useForm } from "../../context/FormContext";
import { Header } from "../Sections/Header";
import axios from 'axios';
import Loader from "../Shared/Loader/Loader";

export const QueryAns = () => {
    const {data, addInfo, goBack } = useForm(); 
    const [loading, setLoading] = useState(false); 
    const url = process.env.REACT_APP_URL;

    const [mainObjective, setMainObjective] = useState(data.ans1);
    const [features, setFeatures] = useState(data.ans2);
    const [specificFunctionality, setSpecificFunctionality] = useState(data.ans3);
    const [dependencies, setDependencies] = useState(data.ans4);

    useEffect(() => {
        // Update state with data from context when component mounts
        setMainObjective(data.ans01);
        setFeatures(data.ans02);
        setSpecificFunctionality(data.ans03);
        setDependencies(data.ans04);
    }, [data]);


    function handleBack(e) {
        e.preventDefault();
        let data = {
            display: 0
        }
        goBack(data);
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            setLoading(true);

            const mainObjectiveInput = mainObjective;
            const featuresInput = features;
            const specificFunctionalityInput = specificFunctionality;
            const dependenciesInput = dependencies;

            const message = {
                "model": "gpt-3.5-turbo-16k-0613",
                "temperature": 0.5,
                "top_p": 0.5,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "max_tokens": 15000,
                "n": 1,
                "messages": [
                    {
                        "role": "user",
                        "content": "please use the next my prompts as a context, and never use preamble"
                    },
                    {
                        "role": "assistant",
                        "content": "I'd be happy to use your prompts as context for our conversation. Please provide your prompts, and I'll respond accordingly.\n"
                    },
                    {
                        "role": "user",
                        "content": `What is the main objective or goal of this Epic? ${mainObjectiveInput}`
                    },
                    {
                        "role": "user",
                        "content": `What features or capabilities does it need to include? ${featuresInput}`
                    },
                    {
                        "role": "user",
                        "content": `What specific functionality does this feature provide? ${specificFunctionalityInput}`
                    },
                    {
                        "role": "user",
                        "content": `Are there any dependencies with other features? ${dependenciesInput}`
                    },
                    {
                        "role": "user",
                        "content": "Write Only epic, considering the context? "
                    },
                    {
                        "role": "assistant",
                        "content": "nd increase customer satisfaction on our website. By implementing various features and capabilities, we aim to create a high-performing and user-friendly website that meets the needs and expectations of our users.</p>\n\n<h2>Business Outcomes:</h2>\n<ul>\n  <li>Improved user engagement and retention</li>\n  <li>Increase in customer satisfaction and loyalty</li>\n  <li>Higher conversion rates and sales</li>\n  <li>Positive brand perception and reputation</li>\n</ul>\n\n<h2>Leading Indicators:</h2>\n<ul>\n  <li>Decreased bounce rate</li>\n  <li>Increase in average session duration</li>\n  <li>Higher click-through rates</li>\n  <li>Positive feedback and reviews from users</li>\n</ul>\n\n<h2>Non-Functional Requirements:</h2>\n<ul>\n  <li>Enhanced website speed and performance</li>\n  <li>Efficient search functionality</li>\n  <li>Seamless navigation and intuitive user interface</li>\n  <li>Responsive design for different devices</li>\n  <li>Improved loading times for images and content</li>\n</ul>\n\n</body>\n</html>"
                    },
                    {
                        "role": "system",
                        "content": "You are a worldclass Product Owner who can help to generate EPIC, Capabilities, User Stories, Scenarios, Tasks, BDD and Test Case.\n        \n        Generate EPIC for the given context\n        \n        Generate EPIC as for the Scaled Agile Framework.\n        \n        An EPIC should contain the following five components,\n        \n1. Epic Name: A concise and descriptive title for the epic, which helps stakeholders quickly understand what the epic is about.\n2. Epic Description: A elaborate narrative or explanation of the epic's purpose, context, and scope. This provides a comprehensive understanding of why the epic is important and what it aims to achieve. This also offers a thorough understanding of the epic's significance and objectives. \n3. Business Outcomes: Clearly defined business objectives or results that the epic is expected to deliver. These outcomes should align with the organization's strategic goals and provide value.\n4. Leading Indicators: Metrics or key performance indicators (KPIs) that serve as early indicators of progress or success for the epic. Leading indicators help track the epic's impact and effectiveness.\n5. Non-Functional Requirements: Requirements that describe the characteristics and qualities of the system or product that are not related to specific functionality. This may include performance, security, scalability, reliability, and other non-functional aspects. \n Give me the response as json object like below format - {\n  \"epicName\": \"\",\n  \"epicDescription\": \"\",\n  \"businessOutcomes\": [],\n  \"leadingIndicators\": [],\n  \"nonFunctionalRequirements\": []\n The ultimate outcome of the conversation will be in json format }"
                    }
                ],
            }
            const response = await axios.post(
                `${url}callOpenAIEpic`,
                message,
            );

            const responseData = response.data;
            console.log(responseData);
            let newData = {
                ans01:mainObjectiveInput,
                ans02:featuresInput,
                ans03:specificFunctionalityInput,
                ans04:dependenciesInput,
                accumulatedResponse: responseData,
                display: 2
            }
            addInfo(newData);
        } catch (error) {
            console.error("Error:", error.message);
        }finally {
            setLoading(false); 
        }
    };

    return (
        <div>
            <Header head="Basic Queries" para="Begin by answering a few questions." />
            <main>
            {loading && <Loader />} {/* Render Loader component if loading state is true */}
                {!loading && (
                <form onSubmit={handleSubmit} className="flex flex-col mt-8" autoComplete="off">
                    <label className="mb-1" htmlFor="ans1">1. What is the main objective or goal of this Epic?</label>
                    <textarea
                        id="ans1"
                        className="border-[1px] text-sm py-2 px-4 rounded-[6px] mb-5"
                        value={mainObjective}
                        onChange={(e) => setMainObjective(e.target.value)}
                        placeholder="Enter your answer here..."
                        required
                    />

                    <label className="mb-1" htmlFor="ans2"> 2. What features or capabilities does it need to include?</label>
                    <textarea
                        id="ans2"
                        className="border-[1px] text-sm py-2 px-4 rounded-[6px] mb-5"
                        value={features}
                        onChange={(e) => setFeatures(e.target.value)}
                        placeholder="Enter your answer here..."
                        required
                    />

                    <label className="mb-1" htmlFor="ans3">3. What specific functionality does this feature provide?</label>
                    <textarea
                        id="ans3"
                        className="border-[1px] text-sm py-2 px-4 rounded-[6px] mb-5"
                        value={specificFunctionality}
                        onChange={(e) => setSpecificFunctionality(e.target.value)}
                        placeholder="Enter your answer here..."
                    />

                    <label className="mb-1" htmlFor="ans4">4. Are there any dependencies with other features?</label>
                    <textarea
                        id="ans4"
                        className="border-[1px] text-sm py-2 px-4 rounded-[6px] mb-5"
                        value={dependencies}
                        onChange={(e) => setDependencies(e.target.value)}
                        placeholder="Enter your answer here..."
                    />

                    <div className="mt-[20%]">    
                        <button onClick={handleBack} className="text-slate-400 hover:text-blue-900">Go Back</button>
                        <button type="submit" className="py-3 float-right ml-auto hover:bg-blue-900 bg-blue-950 text-sm text-white w-[110px] rounded-lg">Next Step</button>
                    </div>
                </form>
            )}
            </main>
        </div>
    )
}
