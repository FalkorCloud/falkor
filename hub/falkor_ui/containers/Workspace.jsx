import React, { Component, PropTypes } from "react";
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import MainSection from '../components/MainSection';
import * as TodoActions from '../actions/todos';

import mui, {AppBar, Styles} from 'material-ui';

import IconButton from 'material-ui/IconButton';
import IconMenu from 'material-ui/IconMenu';
import MenuItem from 'material-ui/MenuItem';
import MoreVertIcon from 'material-ui/svg-icons/navigation/more-vert';
import NavigationClose from 'material-ui/svg-icons/navigation/close';

import {Tabs, Tab} from 'material-ui/Tabs';

import FontIcon from 'material-ui/FontIcon';
import ActionFlightTakeoff from 'material-ui/svg-icons/action/flight-takeoff';

import * as FalkorActions from '../actions/falkor';

import Paper from 'material-ui/Paper';


const style = {
  minHeight: 100,
  width: '66%',
  marginTop: 0,
  display: 'block',
  marginLeft: 'auto',
  marginRight: 'auto',
  paddingBottom: 60
};


const styles = {
  headline: {
    fontSize: 24,
    paddingTop: 16,
    marginBottom: 12,
    fontWeight: 400
  }
};

class Workspace extends Component {
  
  handleClose() {
    this.context.router.push('/');
  }
  
  componentDidMount() {
     console.log('componentWillReceiveProps', this.props.workspaces);
     if (this.props.workspaces.length) {
      this.context.store.dispatch(FalkorActions.select(this.props.workspaces[0].id));
     }
  }

  componentWillReceiveProps(nextProps) {
    console.log('componentWillReceiveProps', nextProps.workspaces);
    if (nextProps.workspaces.length && (!this.props.workspaces.length || (nextProps.workspaces[0].id !== this.props.workspaces[0].id))) {
     this.context.store.dispatch(FalkorActions.select(nextProps.workspaces[0].id));
     console.log('componentWillReceiveProps dispatch', nextProps.workspaces[0].id);
    }
  }
  
  render() {
    const { workspaces, actions, state } = this.props;
    let workspace = workspaces[0] || {name: state};
    if (!workspace.files) {
      workspace.files = [];
    }
    console.log("render", workspace);
    let title = workspace.name;

    return (
      <div>
        <header className="header">
          <AppBar style={{flexWrap: 'wrap'}}
              title={title}
              iconElementLeft={<IconButton onClick={this.handleClose.bind(this)} ><NavigationClose /></IconButton>}
              iconElementRight={
                <IconMenu
                  iconButtonElement={
                    <IconButton><MoreVertIcon /></IconButton>
                  }
                  targetOrigin={{horizontal: 'right', vertical: 'top'}}
                  anchorOrigin={{horizontal: 'right', vertical: 'top'}}
                >
                  <MenuItem primaryText="Refresh" />
                  <MenuItem primaryText="Help" />
                  <MenuItem primaryText="Sign out" />
                </IconMenu>
              }
            >
            <Tabs style={{width: '100%'}}>
              <Tab icon={<ActionFlightTakeoff />} />
              <Tab icon={<ActionFlightTakeoff />} />
              <Tab icon={<ActionFlightTakeoff />} />
            </Tabs>
            
          </AppBar>
          <Paper style={style} zDepth={1}>
              {workspace.files.map(file =>
                <div>--{file.name}</div>
              )}
          </Paper>
        </header>
      </div>
    );
  }
}


Workspace.contextTypes = {
    router: React.PropTypes.object,
    store: React.PropTypes.object
};

Workspace.propTypes = {
  workspaces: PropTypes.array.isRequired,
  actions: PropTypes.object.isRequired
};

function getSelectedWorkspace(workspaces, name) {
  let filtered = workspaces.filter(w => w.name === name);
  return filtered;
}

function mapStateToProps(state, ownProps) {
  return {
    workspaces: getSelectedWorkspace(state.workspaces.workspaces, ownProps.params.workspaceName),
    status: state.workspaces.state
  };
}

function mapDispatchToProps(dispatch) {
  return {
    actions: bindActionCreators(FalkorActions, dispatch)
  };
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Workspace);
