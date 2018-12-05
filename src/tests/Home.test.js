import React from 'react';
import Home from '../components/component';
import renderer from 'react-test-renderer';

it('renders', () => {
  const tree = renderer
    .create(<Home/>)
    .toJSON();
  expect(tree).toMatchSnapshot();
});
