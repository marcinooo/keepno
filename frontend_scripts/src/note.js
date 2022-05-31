// import { Modal } from 'bootstrap';
import { alert } from './alerts';
import { getNoteIdFromUrl, unpackReceivedError } from './utils';

window.addEventListener('load', function() {
    const noteId = getNoteIdFromUrl();
    console.log(noteId);
    const entriesScroller = document.querySelector("#entries");
    const entriesTemplate = document.querySelector('#entries-template');
    const entriesLoadingSpiner = document.querySelector('#entries-loading-spiner');
    const addEntryModal = new bootstrap.Modal(document.querySelector('#addEntryModal'));
    const deleteEntryModal = document.querySelector('#deleteEntryModal');
    const deleteEntryModalObject = new bootstrap.Modal(deleteEntryModal);
    const deleteEntryButton = deleteEntryModal.querySelector('#deleteEntryButton');
    const saveBtn = document.querySelector('#save-entry');
    const updateEntryModal = document.querySelector('#updateEntryModal');
    const updateEntryModalObject = new bootstrap.Modal(updateEntryModal);
    const updateEntryButton = updateEntryModal.querySelector('#updateEntryButton');
    let nextEpage = 1;
    let hasNextEntries = true;

    /** Event triggered to load few entries from database to fill opened page. */
    const loadEntriesAfterPageOpeningEvent = new Event('loadEntriesAfterPageOpeningEvent');

    /** QUILL Editors */
    const saveQuill = new Quill('#add-editor-container', {
      modules: {
        syntax: true,
        toolbar: '#add-toolbar-container'
      },
      placeholder: 'Compose an epic...',
      theme: 'snow'
    });
    const updateQuill = new Quill('#update-editor-container', {
      modules: {
        syntax: true,
        toolbar: '#update-toolbar-container'
      },
      placeholder: 'Compose an epic...',
      theme: 'snow'
    });


    /**
     * Fills passed template with entry's data
     * @param template template to fill
     * @param entry entry object
     * @returns filled template
     */
     function fillEntryTemplateClone(template, entry) {
      template.querySelector("#content").innerHTML = entry.content;
      template.querySelector("#created").innerHTML = entry.created; //moment(entry.created).fromNow();
      const deleteEntryLink = template.querySelector("#deleteEntryLink");
      deleteEntryLink.id = `deleteMobalOpenButton${entry.id}`;
      deleteEntryLink.dataset.entryid = entry.id;
      const updateEntryLink = template.querySelector("#updateEntryLink");
      updateEntryLink.id = `updateMobalOpenButton${entry.id}`;
      updateEntryLink.dataset.entryid = entry.id;
      const entryRow = template.querySelector("#entryRow");
      entryRow.id = `entry${entry.id}`;
      return template
    }


    /** 
     * Adds single entry as last element in entryScroller container.
     * @param entry entry to add
     * @param template template with html structure for single entry
     * @param scroller container for list of entries
     */  
    function addEntryToTheBottomOfEntryScroller(entry, template, scroller) {
      let template_clone = template.content.cloneNode(true);
      template_clone = fillEntryTemplateClone(template_clone, entry);
      scroller.appendChild(template_clone);
    }


    /** 
     * Adds single entry as first element in entriesScroller container.
     * @param entry entry to add
     * @param template template with html structure for single entry
     * @param scroller container for list of entries
     */
    function addEntryToTheTopOfEntryScroller(entry, template, scroller) {
      let template_clone = template.content.cloneNode(true);
      template_clone = fillEntryTemplateClone(template_clone, entry)
      scroller.insertBefore(template_clone, scroller.firstChild.nextSibling);  // to check
    }


    /**
     * Checks if document's scrollbar is visible.
     * @returns true if scrollbar is visible, otherwise false
     */
    function documentScrollbarIsActive() {
      return document.documentElement.scrollHeight > document.documentElement.clientHeight;
    }


    /**
     * Unpacks received entries.
     * @param data data recived from server
     */
    function unpackReceivedEntriesData(data) {
      for (let i = 0; i < data.entries.length; i++) {
        addEntryToTheBottomOfEntryScroller(data.entries[i], entriesTemplate, entriesScroller)
      }
      if (data.has_next) {
        nextEpage = data.next_num;
        hasNextEntries = true;
      } else {
        hasNextEntries = false;
        entriesLoadingSpiner.style.display = "none";
      }
    }


    /** 
     * Observer for entry section. It triggers get request to obtain new entries when user is scrolling list of entries. 
     */        
    const intersectionObserver = new IntersectionObserver(entries => {
      if (entries[0].intersectionRatio <= 0) { return; }
      if (hasNextEntries) {
        fetch(`/api/notes/${noteId}/entries?epage=${nextEpage}`)
        .then(function(response) {
          return response.json();
        })
        .then(function(data) {
          unpackReceivedEntriesData(data);
        })
        .catch(function (error) {
          console.log(error);
          alert.error("There was a problem. Entries couldn't be downloaded.");
        });
      }
    });


    /**
     * 'loadEntriesAfterPageOpeningEvent' event listener which triggers get request to obtain new entries to fill opened page.
     */
    document.addEventListener('loadEntriesAfterPageOpeningEvent', function(event ) {
      if (hasNextEntries) {
        fetch(`/api/notes/${noteId}/entries?epage=${nextEpage}`)
        .then(function(response) {
          return response.json();
        })
        .then(function(data) {
          unpackReceivedEntriesData(data);
          if (! documentScrollbarIsActive()) {
            document.dispatchEvent(loadEntriesAfterPageOpeningEvent);
          } else {
            intersectionObserver.observe(entriesLoadingSpiner);
          }
        })
        .catch(function (error) {
          console.log(error);
          alert.error("There was a problem. Entries couldn't be downloaded.");
        });
      }
    });

    
    /**
     * 'click' event listener which triggers post request to add new entry.
     */
    saveBtn.addEventListener('click', function(e){
      // Check if user entered data
      const entryContent = saveQuill.root.innerHTML.trim() === '<p><br></p>' ? "" : saveQuill.root.innerHTML;
      fetch(`/api/notes/${noteId}/entries`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({content: entryContent, note_id: noteId}),
      })
      .then(function(response){
        return response.json();
      })
      .then(function(data) {
        if (data.entry) {
          addEntryToTheTopOfEntryScroller(data.entry, entriesTemplate, entriesScroller)
          saveQuill.root.innerHTML = '';
          addEntryModal.hide();
          alert.success("New entry has been added successfully!");
        } else {
          const errorMessage = unpackReceivedError(data.error, 'Your entry was not added:<br/>');
          alert.error(errorMessage);
        }
      })
      .catch(function(error) {
        console.log(error);
        alert.error("There was a problem. The entry was not added!");
      });
    })


    /**
     * 'show.bs.modal' event listener which reads entry id and passes it to delete confirmation button.
     */
    deleteEntryModal.addEventListener('show.bs.modal', function(event) {
      const button = event.relatedTarget;
      const entryId = button.getAttribute('data-entryid');
      deleteEntryButton.dataset.entryid = entryId;
    });


    /**
     * 'click' event listener which triggers delete request to delete entry.
     */
    deleteEntryButton.addEventListener('click', function(event) {
      fetch(`/api/notes/${noteId}/entries/${event.target.dataset.entryid}`, {
        method: 'DELETE',
      })
      .then(function(response) {
        return response.json();
      })
      .then(function(data) {
        if (data.entry) {
          const entryElement = document.getElementById(`entry${event.target.dataset.entryid}`);
          deleteEntryModalObject.hide();
          entryElement.remove();
          alert.success("Entry has been deleted successfully!");
        } else {
          const errorMessage = unpackReceivedError(data.error, 'Your entry was not deleted:<br/>');
          alert.error(errorMessage);
        }
      })
      .catch(function (error) {
        console.log(error);
        alert.error("There was a problem. Entry couldn't be deleted.");
      });
    })


    /**
     * 'show.bs.modal' event listener which reads entry id and passes it to update confirmation button.
     */
    updateEntryModal.addEventListener('show.bs.modal', function(event) {
      const button = event.relatedTarget;
      const entryId = button.getAttribute('data-entryid');
      updateEntryButton.dataset.entryid = entryId;
      const entryContent = document.querySelector(`#entry${entryId} #content`);
      updateQuill.root.innerHTML = entryContent.innerHTML;
    });

    
    /**
     * 'click' event listener which triggers put request to update entry.
     */
    updateEntryButton.addEventListener('click', function(event){
      // Check if user entered data
      const newEntryContent = updateQuill.root.innerHTML.trim() === '<p><br></p>' ? "" : updateQuill.root.innerHTML;
      fetch(`/api/notes/${noteId}/entries/${event.target.dataset.entryid}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({content: newEntryContent, note_id: noteId}),
      })
      .then(function(response){
        return response.json();
      })
      .then(function(data) {
        if (data.entry) {
          const entryContent = document.querySelector(`#entry${event.target.dataset.entryid} #content`);
          entryContent.innerHTML = newEntryContent;
          updateQuill.root.innerHTML = '';
          updateEntryModalObject.hide();
          alert.success("Entry has been updated successfully!");
        } else {
          const errorMessage = unpackReceivedError(data.error, 'Your entry was not updated:<br/>');
          alert.error(errorMessage);
        }
      })
      .catch(function(error) {
        console.log(error);
        alert.error("There was a problem. The entry was not updated!");
      });
    })


    // Trigger first event to obtain first notes.
    document.dispatchEvent(loadEntriesAfterPageOpeningEvent);
  });

