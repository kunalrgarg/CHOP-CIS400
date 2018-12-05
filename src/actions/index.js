import fetch from 'isomorphic-fetch';
import config from '../config/client';

export const updateSearchTerm = (newSearchTerm) => ({
  type: 'UPDATE_SEARCH_TERM',
  newSearchTerm
});

export const updateSearchType = (newSearchType) => ({
    type: 'UPDATE_SEARCH_TYPE',
    newSearchType
});

export const requestSearchSent = () => ({
  type: 'REQUEST_SEARCH_SENT'
});

export const requestSearchFailed = (error) => ({
  type: 'REQUEST_SEARCH_FAILED', error
});

export const requestSearchSuccess = (results) => ({
  type: 'REQUEST_SEARCH_SUCCESS', results
});

export function requestSearch(searchTerm, searchType) {
  return function(dispatch) {
    dispatch(requestSearchSent());
    return fetch(`${config.endpoint}search/${searchTerm}&type=${searchType}`)
      .then(response => response.json()
        .then(json => ({
          status: response.status,
          json
        })))
      .then(({ status, json }) => {
        if (status >= 400) dispatch(requestSearchFailed());
        else dispatch(requestSearchSuccess(json))
      }, err => { dispatch(requestSearchFailed(err))  })
  }
}


