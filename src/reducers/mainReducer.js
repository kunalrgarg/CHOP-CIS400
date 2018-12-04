
const initialState = {
  searchTerm: '',
  results: null,
  inProgress: false,
  errorMessage: null,
};

const mainReducer = (state = initialState, action) => {
  switch (action.type) {
    case 'UPDATE_SEARCH_TERM':
      return Object.assign({}, state, {
        searchTerm: action.newSearchTerm,
      });
    case 'REQUEST_SEARCH_SENT':
      return Object.assign({}, state, {
        inProgress: true,
      });
    case 'REQUEST_SEARCH_FAILED':
      return Object.assign({}, state, {
        inProgress: false,
        errorMessage: action.error,
      });
    case 'REQUEST_SEARCH_SUCCESS':
      return Object.assign({}, state, {
        results: action.results,
        inProgress: false,
        errorMessage: null,
      });
    default:
      return state;
  }
};

export default mainReducer;
