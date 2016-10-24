
const initialState = {
  state: 'connecting',
  workspaces: []
};

export default function workspaces(state = initialState, action) {
  switch (action.type) {
  case 'UPDATE_WORKSPACE':
    let workspaces = state.workspaces;
    let workspace = action.data.data;
    let index = workspaces.findIndex(w => w.id === workspace.id)
    if (index > -1) {
      workspaces[index] = workspace;
    }
    console.log('UPDATE_WORKSPACE', action);
    return {state: 'connected', workspaces: workspaces};
  case 'WORKSPACES':
    return {state: 'connected', workspaces: action.data.data.workspaces};
  default:
    return state;
  }
}
