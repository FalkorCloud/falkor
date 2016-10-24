import { combineReducers } from 'redux';
import todos from './todos';
import workspaces from './workspaces';

const rootReducer = combineReducers({
    todos,
    workspaces
});

export default rootReducer;
