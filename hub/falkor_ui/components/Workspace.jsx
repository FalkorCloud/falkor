import React, { Component, PropTypes } from "react";

import Avatar from 'material-ui/Avatar';
import IconButton from 'material-ui/IconButton';
import MoreVertIcon from 'material-ui/svg-icons/navigation/more-vert';
import IconMenu from 'material-ui/IconMenu';
import MenuItem from 'material-ui/MenuItem';
import {List, ListItem} from 'material-ui/List';

const iconButtonElement = (
  <IconButton touch={true} tooltipPosition="bottom-left" tooltip="more">
    <MoreVertIcon />
  </IconButton>
);

const rightIconMenu2 = (
  <IconMenu iconButtonElement={iconButtonElement}>
    <MenuItem>Reply</MenuItem>
    <MenuItem>Forward</MenuItem>
    <MenuItem>Delete</MenuItem>
  </IconMenu>
);

class Workspace extends Component {
    rightIconMenu(href) {
      return (
        <IconMenu iconButtonElement={iconButtonElement}>
          <MenuItem href={href} target="_blank" >Open</MenuItem>
          <MenuItem>Stop</MenuItem>
          <MenuItem>Delete</MenuItem>
        </IconMenu>
      );
    }
    render() {
        const { workspace, select } = this.props;
        let right = this.rightIconMenu('http://'+workspace.url+'.'+/*window.location.host*/'localhost.be:8080');
        return (
            <ListItem
                onClick={select}
                leftAvatar={<Avatar>{workspace.name.substring(0,1).toUpperCase()}</Avatar>}
                insetChildren={false}
                primaryText={workspace.name}
                secondaryText={workspace.state.IPAddress}
                rightIconButton={right}
              />
        );
    }
}
   
Workspace.propTypes = {
  workspace: PropTypes.object.isRequired,
  select: PropTypes.func.isRequired
};   

export default Workspace;