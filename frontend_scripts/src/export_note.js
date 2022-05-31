import { alert } from './alerts';

window.addEventListener('load', function() {
    const noteId = "{{ note.id }}";
    const collapseProgress = document.querySelector('#collapseProgress');
    const collapseResult = document.querySelector('#collapseResult');
    const downloadLink = document.querySelector('#downloadLink');
    const generateButton = document.querySelector('#generateButton');
    const progressBar = document.querySelector('#progressBar');
    const collapseProgressObject = new bootstrap.Collapse(collapseProgress, {
      toggle: false
    });
    const collapseResultObject = new bootstrap.Collapse(collapseResult, {
      toggle: false
    });

    /**
     * 'click' event listener which triggers pdf generation request.
     */
    generateButton.addEventListener('click', function(event) {
      generateButton.disabled = true;
      collapseProgressObject.show();
      fetch(`/api/notes/${noteId}/export/pdf`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      .then(function(response){
        return response.json();
      })
      .then(function(data) {
        console.log(data);
        if (data.report_status == "started") {
          updateProgress(`/api/task/${data.task_id}`)
        } else {
          const errorMessage = `Your note has been not dumped to PDF:<br/><ul><li>${data.error}</li></ul>`;
          alert.error(errorMessage);
        }
      })
      .catch(function(error) {
        console.log(error);
        alert.error("There was a problem. Your note has been not dumped to PDF!");
      });
    });

    /**
     * Updates progress bar for scheduled generation of pdf.
     * @param progressUrl progressUrl url of endpoint to get progress value
     */
    function updateProgress (progressUrl) {
      fetch(progressUrl)
      .then(function(response) {
        return response.json();
      })
      .then(function(data) {
        progressBar.style.width = `${data.progress}%`;
        if (data.status === "PROGRESS") {
          setTimeout(updateProgress, 500, progressUrl);
        } else if (data.status === "SUCCESS") {
          downloadLink.href = data.result;
          collapseResultObject.show();
          collapseProgressObject.hide();
          generateButton.disabled = false;
          alert.success("Note has been generated successfully!");
        } else {
          collapseProgressObject.hide();
          generateButton.disabled = false;
          alert.error("There was a problem. Your note has been not dumped to PDF!");
        }
      })
      .catch(function(error) {
        console.log(error);
        alert.error("There was a problem. Your note has been not dumped to PDF!");
      });
    }

  });
