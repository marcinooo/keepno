window.addEventListener('load', function() {

  const notesScroller = document.querySelector('#notes');
  const notesTemplate = document.querySelector('#notesTemplate');
  const notesLoadingSpiner = document.querySelector('#notesLoadingSpiner');
  const addNoteForm = document.getElementById('addNoteForm');
  const addNoteModal = new bootstrap.Modal(document.getElementById('addNoteModal'));
  let nextNpage = 1;
  let hasNextNotes = true;

  /** Event triggered to load few notes from database to fill opened page. */
  const loadNotesAfterPageOpeningEvent = new Event('loadNotesAfterPageOpeningEvent');

  /**
   * Fills passed template with note's data
   * @param template template to fill
   * @param note note object
   * @returns filled template
   */
  function fillNoteTemplateClone(template, note) {
    template.querySelector("#noteTitle").innerHTML = note.title;
    template.querySelector("#noteDescription").innerHTML = note.description;
    template.querySelector("#noteDate").innerHTML = moment(note.updated).format('MMM\xa0Do\xa0YY');
    template.querySelector("#noteLink").href = `/notes/${note.id}`;
    return template
  }


  /** 
   * Adds single note as last element in notesScroller container.
   * @param note note to add
   * @param template template with html structure for single note
   * @param scroller container for list of notes
   * @param activeCurrentNote it adds darker backgroud to note element if it is true
   */  
  function addNoteToTheBottomOfNoteScroller(note, template, scroller, activeCurrentNote=true) {
    let templateClone = template.content.cloneNode(true);
    fillNoteTemplateClone(templateClone, note);
    const noteLink = templateClone.querySelector("#noteLink");
    if (activeCurrentNote) { 
      const displaiedNoteId = getNoteIdFromUrl(); 
      if (displaiedNoteId == note.id) { noteLink.style.background = "rgb(233, 233, 233)"; }
    }
    scroller.appendChild(templateClone);
  }


  /** 
   * Adds single note as first element in notesScroller container.
   * @param note note to add
   * @param template template with html structure for single note
   * @param scroller container for list of notes
   */  
   function addNoteToTheTopOfNoteScroller(note, template, scroller) {
    let templateClone = template.content.cloneNode(true);
    templateClone = fillNoteTemplateClone(templateClone, note);
    scroller.insertBefore(templateClone, scroller.firstChild.nextSibling);
  }


  /** 
   * Returns note id from url.
   * @return id of note or empty string
   */
  function getNoteIdFromUrl() {
    const url = window.location.href;
    const lastIndexOfSlash = url.lastIndexOf('/');
    const noteId = url.slice(lastIndexOfSlash+1).match(/^[0-9]+/g);
    if (noteId.length > 0) {
      return noteId[0]
    }
    return '';
  }


  /**
   * Checks if sidebar's scrollbar is visible.
   * @returns true if scrollbar is visible, otherwise false
   */
   function sidebarScrollbarIsActive() {
    const sidebarBody = document.getElementById('sidebarBody');
    return sidebarBody.scrollHeight > sidebarBody.clientHeight;
  }


  /**
   * Unpack received notes.
   * @param data data recived from server
   */
  function unpackReceivedNotesData(data) {
    for (var i = 0; i < data.notes.length; i++) {
      addNoteToTheBottomOfNoteScroller(data.notes[i], notesTemplate, notesScroller);
    }
    if (data.has_next) {
      nextNpage = data.next_num;
      hasNextNotes = true;
    } else {
      hasNextNotes = false;
      notesLoadingSpiner.style.display = "none";
    }
  }


  /** 
   * Observer for note section. It triggers get request to obtain new notes when user is scrolling list of notes. 
   */   
  const intersectionNotesObserver = new IntersectionObserver(function (notes) {
  if (notes[0].intersectionRatio <= 0) { return; }
    if (hasNextNotes) {
      fetch(`/api/notes?npage=${nextNpage}`)
      .then(function(response) {
        return response.json();
      })
      .then(function(data) {
        unpackReceivedNotesData(data);
      })
      .catch(function(error) {
        console.log(error);
        alert.error("There was a problem. Notes couldn't be downloaded.");
      });
    }
  });


  /**
   * 'loadNotesAfterPageOpeningEvent' event listener which triggers get request to obtain new notes to fill opened page.
   */
  document.addEventListener('loadNotesAfterPageOpeningEvent', function(event) {
    if (hasNextNotes) {
      fetch(`/api/notes?npage=${nextNpage}`)
      .then(function(response) {
        return response.json();
      })
      .then(function(data) {
        unpackReceivedNotesData(data);
        if (! sidebarScrollbarIsActive()) {
          document.dispatchEvent(loadNotesAfterPageOpeningEvent);
        } else {
          intersectionNotesObserver.observe(notesLoadingSpiner);
        }
      })
      .catch(function(error) {
        console.log(error);
        alert.error("There was a problem. Notes couldn't be downloaded.");
      });
    }
  });

  /**
   * 'submit' event listener which triggers post request add new note.
   */
  addNoteForm.addEventListener('submit', function(event) {
    event.preventDefault();
    const title = document.querySelector('#newNoteTitle').value;
    const description = document.querySelector('#newNoteDescription').value;
    fetch('/api/notes', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({title, description}),
    })
    .then(function(response) {
      return response.json();
    })
    .then(function(data) {
      if (data.note) {
        addNoteModal.hide();
        addNoteToTheTopOfNoteScroller(data['note'], notesTemplate, notesScroller);
        alert.success("New note has been added successfully!");
      } else {
        const message = unpackReceivedError(data.error, 'Your note was not added:<br/>');
        alert.error(message);
      }
    })
    .catch(function(error) {
      console.log(error);
      alert.error("There was a problem. The note was not added!");
    });

  });


  // Trigger first event to obtain first notes.
  document.dispatchEvent(loadNotesAfterPageOpeningEvent);

});
