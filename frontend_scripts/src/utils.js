/**
 * Unpack received errors.
 * @param error error data recived from server
 * @param header text displaied before errors information
 * @returns prepared html body
 */
 export function unpackReceivedError(error, header) {
  const keys = Object.keys(error);
  let message = header + '<ul>';
  if(typeof error === 'string') {
    return message + '<li>' + error + '</li></ul>';
  }
  for (let i = 0; i < keys.length; i++) {
    message += '<li>';
    if (error[keys[i]].length == 1) {
      message += error[keys[i]][0];
    } else {
      message += '<ul>';
      for (let j = 0; j < error[keys[i]].length; j++) {
        message += `<li>${error[keys[i]][j]}</li>`;
      }
      message += '</ul>';
    }
    message += '</li>';
  }
  message += '</ul>';
  return message;
}
  

/** 
 * Returns note id from url.
 * @return id of note or empty string
 */
export function getNoteIdFromUrl() {
  const url = window.location.href;
  try {
    const noteId = url.match(/notes\/\d+/g)[0].split('/')[1];
    if (noteId.length > 0) {
      return noteId[0];
    }
  } catch (error) { }
  return '';
}
