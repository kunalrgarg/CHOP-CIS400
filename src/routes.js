import React from 'react';
import { Route, Switch } from 'react-router-dom';
import App from './components/App';
import Home from './components/Home';

const routes = (
  <App>
    <Switch>
      <Route exact path='/' component={Home} />
    </Switch>
  </App>
);

export { routes };
