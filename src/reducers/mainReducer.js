
const initialState = {
  searchTerm: '',
  searchType: 'keyword',
  results: null,
  recResults: null,
  inProgress: false,
  errorMessage: null,
  recInProgress: false,
  recErrorMessage: null,
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
    case 'REQUEST_REC_SENT':
      return Object.assign({}, state, {
        recInProgress: true,
      });
    case 'REQUEST_REC_FAILED':
      return Object.assign({}, state, {
        recInProgress: false,
        recErrorMessage: action.error,
      });
    case 'REQUEST_REC_SUCCESS':
      return Object.assign({}, state, {
        recResults: action.recResults,
        recInProgress: false,
        recErrorMessage: null,
      });
    default:
      return state;
  }
};

export default mainReducer;
