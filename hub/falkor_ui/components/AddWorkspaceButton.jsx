import React, { Component, PropTypes } from "react";

import FloatingActionButton from 'material-ui/FloatingActionButton';
import ContentAdd from 'material-ui/svg-icons/content/add';

const styleAddButton = {
    position: 'fixed',
    bottom: 22,
    right: 20
};

class AddWorkspaceButton extends Component {
    render() {
        const { addWorkspace } = this.props;
        return (
            <FloatingActionButton style={styleAddButton}>
              <ContentAdd />
            </FloatingActionButton>
        );
    }
}
   
AddWorkspaceButton.propTypes = {
  addWorkspace: PropTypes.func.isRequired
};   

export default AddWorkspaceButton;
