import React from "react";
import ReactDOM from "react-dom";
import injectTapEventPlugin from "react-tap-event-plugin";
import { createStore } from 'redux';
import { Provider } from 'react-redux';

import App from '../containers/App';
import Workspace from '../containers/Workspace';
import configureStore from '../store/configureStore';

import darkBaseTheme from 'material-ui/styles/baseThemes/darkBaseTheme';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import getMuiTheme from 'material-ui/styles/getMuiTheme';


import { Router, Route, hashHistory } from 'react-router'

//Needed for React Developer Tools
window.React = React;

//Needed for onTouchTap
//Can go away when react 1.0 release
//Check this repo:
//https://github.com/zilverline/react-tap-event-plugin
injectTapEventPlugin();

const store = configureStore();

import * as FalkorActions from '../actions/falkor';
store.dispatch(FalkorActions.connect())

ReactDOM.render(
  //<MuiThemeProvider muiTheme={getMuiTheme(darkBaseTheme)}>
  <MuiThemeProvider>
    <Provider store={store}>
      <Router history={hashHistory}>
          <Route path="/" component={App}/>
          <Route path="/workspaces/:workspaceName" component={Workspace}/>
      </Router>
    </Provider>
  </MuiThemeProvider>,
  document.getElementById("root")
);
