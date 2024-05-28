import { createContext, useContext, useReducer } from "react";
import { FormReduces } from "../reducers/FormReducers";

const initialFormData = {
    name: "",
    projectId: "",
    ans01:"",
    ans02:"",
    ans03:"",
    ans04:"",
    parentKey: "",
    display: 0,
    accumulatedResponse: "",
    storyResponse: "",
    plan: "",
    duration: false,
    service: false,
    storage: false,
    profile: false
}

const FormContext = createContext(initialFormData);

export const FormContextProvider = ({ children }) => {
    const [state, dispatch] = useReducer(FormReduces, initialFormData);
    function addInfo(data) {
        dispatch({
            type: 'ADD_INFO',
            payload: data
        })
    }
    function goBack(data) {
        dispatch({
            type: 'ADD_INFO',
            payload: data
        })
    }
    const value = {
        addInfo,
        goBack,
        data: { ...state }
    }
    return (
        <FormContext.Provider value={value}>
            {children}
        </FormContext.Provider>
    )
}

export const useForm = () => useContext(FormContext);