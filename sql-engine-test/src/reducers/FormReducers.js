export const FormReduces = (state, action) => {
  const { type, payload } = action;

  switch (type) {
    case "ADD_INFO":
      console.log(payload);
      return { ...state, ...payload };
    case "GO_BACK":
      return { ...state, ...payload };
    case "UPDATE_DISPLAY":
      return { ...state, display: action.payload };
    default:
      return "No case found";
  }
};
