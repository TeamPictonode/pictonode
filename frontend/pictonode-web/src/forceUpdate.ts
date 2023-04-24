// GNU AGPL v3 License
// Written by John Nunley

let _forceUpdate: () => void = () => {};

export function forceUpdate() {
  _forceUpdate();
}

export function setForceUpdate(forceUpdate: () => void) {
  _forceUpdate = forceUpdate;
}
