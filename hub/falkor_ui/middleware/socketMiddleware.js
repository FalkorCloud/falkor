import * as actions from '../actions/falkor'

const socketMiddleware = (function(){ 
  let socket = null;

  const onOpen = (ws,store,token) => evt => {
    //Send a handshake, or authenticate with remote end

    //Tell the store we're connected
    store.dispatch(actions.connected());
  }

  const onClose = (ws,store) => evt => {
    //Tell the store we've disconnected
    store.dispatch(actions.disconnected());
  }

  const onMessage = (ws,store) => evt => {
    //Parse the JSON message received on the websocket
    let msg = JSON.parse(evt.data);
    if (actions[msg.event.replace('.', '__')]) {
        console.log("dispatch: '" + msg.event + "'", msg);
        store.dispatch(actions[msg.event.replace('.', '__')](msg));
    } else {
        console.log("Received unknown message event: '" + msg.event + "'", msg);
    }
    /*
    switch(msg.type) {
      case "CHAT_MESSAGE":
        //Dispatch an action that adds the received message to our state
        store.dispatch(actions.messageReceived(msg));
        break;
      default:
        console.log("Received unknown message type: '" + msg.type + "'", msg);
        break;
    }
    */
  }

  return store => next => action => {
      console.log('socketMiddleware', action);
    switch(action.type) {

      //The user wants us to connect
      case 'CONNECT':
        //Start a new connection to the server
        if(socket != null) {
          socket.close();
        }
        //Send an action that shows a "connecting..." status for now
        console.log(actions);
        store.dispatch(actions.connecting());

        //Attempt to connect (we could send a 'failed' action on error)
        socket = new WebSocket(action.url);
        socket.onmessage = onMessage(socket,store);
        socket.onclose = onClose(socket,store);
        socket.onopen = onOpen(socket,store,action.token);

        break;

      //The user wants us to disconnect
      case 'DISCONNECT':
        if(socket != null) {
          socket.close();
        }
        socket = null;

        //Set our state to disconnected
        store.dispatch(actions.disconnected());
        break;

      case 'SELECT_WORKSPACE':
        console.log('SELECT_WORKSPACE', action);
        let data = {event: 'workspaces.select', data: {workspace_id: action.workspace_id}};
        console.log('sending', data);
        socket.send(JSON.stringify(data));
        break;
        
      //Send the 'SEND_MESSAGE' action down the websocket to the server
      case 'SEND_CHAT_MESSAGE':
        socket.send(JSON.stringify(action));
        break;

      //This action is irrelevant to us, pass it on to the next middleware
      default:
        return next(action);
    }
  }

})();

export default socketMiddleware