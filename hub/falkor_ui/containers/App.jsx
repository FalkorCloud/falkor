import React, { Component, PropTypes } from "react";
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import Workspace from '../components/Workspace';
import AddWorkspaceButton from '../components/AddWorkspaceButton';

import * as TodoActions from '../actions/todos';


import mui, {AppBar, Styles} from 'material-ui';

import IconMenu from 'material-ui/IconMenu';
import MenuItem from 'material-ui/MenuItem';
import MoreVertIcon from 'material-ui/svg-icons/navigation/more-vert';
import IconButton from 'material-ui/IconButton';



import Paper from 'material-ui/Paper';
import {List} from 'material-ui/List';


const style = {
  minHeight: 100,
  width: '66%',
  marginTop: 0,
  display: 'block',
  marginLeft: 'auto',
  marginRight: 'auto',
  paddingBottom: 60
};


class App extends Component {

  
  handleOpen(event, workspace) {
    console.log("handleClick", event, workspace, this);
    if (event.target.nodeName === 'BUTTON') {
      event.preventDefault();
      return false;
    }

    const workspaceName = workspace.name;
    const path = `/workspaces/${workspaceName}`;
    this.context.router.push(path);
  }
  
  render() {
    const { todos, workspaces, actions } = this.props;
    /*<Header addTodo={actions.addTodo} />*/
    //<MainSection todos={todos} actions={actions} />
    return (
      <div>
        <AddWorkspaceButton addWorkspace={actions.add} />
        <AppBar title="Falkor" showMenuIconButton={false}
          iconElementRight={
            <IconMenu
              iconButtonElement={
                <IconButton><MoreVertIcon /></IconButton>
              }
              targetOrigin={{horizontal: 'right', vertical: 'top'}}
              anchorOrigin={{horizontal: 'right', vertical: 'top'}}
            >
              <MenuItem primaryText="Add workspace" />
            </IconMenu>
          }
        />
        <Paper style={style} zDepth={1}>
          <List>
            {workspaces.map(workspace =>
              <Workspace key={workspace.id} workspace={workspace} select={(event) => this.handleOpen(event, workspace)} />
            )}
          </List>
        </Paper>
      </div>
    );
  }
}


App.propTypes = {
  actions: PropTypes.object.isRequired
};

App.contextTypes = {
    router: React.PropTypes.object
};

function mapStateToProps(state) {
  return {
    workspaces: state.workspaces.workspaces,
    status: state.workspaces.state
  };
}

import * as FalkorActions from '../actions/falkor';

function mapDispatchToProps(dispatch) {
  return {
    //actions: bindActionCreators(TodoActions, dispatch)
    actions: bindActionCreators(FalkorActions, dispatch)
  };
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(App);
