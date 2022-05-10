/**
 * Utils for rendering alerts in app. 'alerts.html' is required to proper working.
 * Usage: alert.success("Your super log!");
 */


/**
 * Alert object with differnt types of logging.
 */
const alert = (function(){

  /** Alerts types */
  const CATEGORIES = {
    SUCCESS: 'SUCCESS',
    INFO: 'INFO',
    WARNING: 'WARNING',
    ERROR: 'ERROR'
  }


  /**
   * Returns class name for alert's toast element.
   * @param category category alert's type to return proper class
   * @returns class name if class name was found for given category, otherwise empty string
   */
  function getAlertToastClass(category) {
    if (category === CATEGORIES.SUCCESS) { return ' border-success' };
    if (category === CATEGORIES.INFO) { return ' border-info' };
    if (category === CATEGORIES.WARNING) { return ' border-warning' };
    if (category === CATEGORIES.ERROR) { return ' border-danger' };
    return '';
  }


  /**
   * Returns class name for alert's header element.
   * @param category category alert's type to return proper class
   * @returns class name if class name was found for given category, otherwise empty string
   */
  function getAlertHeaderClass(category) {
    if (category === CATEGORIES.SUCCESS) { return ' text-success' };
    if (category === CATEGORIES.INFO) { return ' text-info' };
    if (category === CATEGORIES.WARNING) { return ' text-warning' };
    if (category === CATEGORIES.ERROR) { return ' text-danger' };
    return '';
  }


  /**
   * Creates alert element and shows it in document.
   * @param category category alert's type to return proper class
   * @param icon icon to insert in alert 
   * @param body text to display in alert body 
   * @param header text to display in alert header
   */
  function createAlert(category, icon, body, header) {
    const alertTemplate = document.querySelector('#alertTemplate');
    let alertTemplateClone = alertTemplate.content.cloneNode(true);
    const alertHeader = alertTemplateClone.querySelector("#alertHeader");
    alertHeader.innerHTML = header;
    alertHeader.className += getAlertHeaderClass(category);
    alertTemplateClone.querySelector("#alertIcon").innerHTML = icon;
    alertTemplateClone.querySelector("#alertBody").innerHTML = body;
    const alertToast = alertTemplateClone.querySelector("#alertToast");
    alertToast.className += getAlertToastClass(category);
    alertToast.id =  Math.random().toString(36);
    const alerts = document.querySelector("#alerts");
    alerts.appendChild(alertTemplateClone);
    const notificationToast = new bootstrap.Toast(alertToast)
    notificationToast.show();
  }


  return {

    /**
     * Shows success alert.
     * @param message text to display in alert body 
     * @param header text to display in alert header 
     */
    success: function(message, header='Success') {
      const icon = `
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" 
              class="bi bi-check-circle-fill text-success" viewBox="0 0 16 16">
          <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 
                   0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
        </svg>
      `;
      createAlert(CATEGORIES.SUCCESS, icon, message, header);
    },

    /**
     * Shows info alert.
     * @param message text to display in alert body 
     * @param header text to display in alert header 
     */
    info: function(message, header='Info') {
      const icon = `
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" 
             class="bi bi-info-circle-fill text-info" viewBox="0 0 16 16">
          <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 
                   .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 
                   5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"/>
        </svg>
      `;
      createAlert(CATEGORIES.INFO, icon, message, header);
    },

    /**
     * Shows warning alert.
     * @param message text to display in alert body 
     * @param header text to display in alert header 
     */
    warning: function(message, header='Warning') {
      const icon = `
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" 
             class="bi bi-exclamation-triangle-fill text-warning" viewBox="0 0 16 16">
          <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 
                   1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 
                   5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
        </svg>
      `;
      createAlert(CATEGORIES.WARNING, icon, message, header);
    },

    /**
     * Shows error alert.
     * @param message text to display in alert body 
     * @param header text to display in alert header 
     */
    error: function(message, header='Error') {
      const icon = `
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" 
             class="bi bi-exclamation-triangle-fill text-danger" viewBox="0 0 16 16">
          <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 
                   1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 
                   5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
        </svg>
      `;
      createAlert(CATEGORIES.ERROR, icon, message, header);
    },

  }
    
})();
