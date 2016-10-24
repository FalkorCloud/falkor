export function connect() {
  //return { type: 'CONNECT', url: "ws://" + window.location.host + "/ws/" };
  return { type: 'CONNECT', url: "ws://localhost.be:8080/ws/" };
}

export function connected() {
  return { type: 'CONNECTION', status: 'connected' };
}

export function connecting() {
  return { type: 'CONNECTING', status: 'connecting' };
}

export function workspaces(data) {
  return { type: 'WORKSPACES', data: data };
}

export function select(workspace_id) {
  return { type: 'SELECT_WORKSPACE', workspace_id };
}

export function add(data) {
  return { type: 'ADD_WORKSPACE', data: data };
}

export function workspaces__select(data) {
  return { type: 'UPDATE_WORKSPACE', data };
}