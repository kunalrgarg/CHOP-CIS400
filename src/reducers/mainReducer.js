
const initialState = {
  searchTerm: '',
  searchType: 'General Keyword',
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
    case 'UPDATE_SEARCH_TYPE':
      return Object.assign({}, state, {
        searchType: action.newSearchType,
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
