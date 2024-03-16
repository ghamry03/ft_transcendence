function fetchMainContent(pageUrl, container) {
  return new Promise((resolve) => {
    fetch(pageUrl)
      .then(response => response.text())
      .then(data => {
        var parser = new DOMParser();
        var doc = parser.parseFromString(data, "text/html").querySelector("body").innerHTML;
        document.getElementById(container).innerHTML = doc;
        resolve();  
      });
  });
}

function injectScript(src, container, id) {
  var scriptElement = document.createElement('script');
  scriptElement.src = src;
  scriptElement.id = id;
  document.getElementById(container).appendChild(scriptElement);
}

function updateStatus(status) {
  fetch('/status/' + status.toString());
}

const cleanScript = {
  'token': () => {
    clearInterval(pid);
  },
  'offline': () => {
    offlineGame.destroy();
    delete(offlineGame);
  },
  'online': () => {
    onlineGame.destroy();
    delete(onlineGame);
  },
  'tournament': () => {
    tournament.destroy();
    delete(tournament);
  },
}

function removeScript(id) {
  script = document.getElementById(id);
  if (script) {
    script.remove();
    cleanScript[id]();
  }
}

const injections = {
  '/home': () => {
    fetchMainContent('/home', 'mainContentArea')
      .then(() => fetchMainContent('/topbar', 'topBar'))
      .then(() => fetchMainContent('/cards', 'homeContentArea'))
      .then(() => injectScript('/static/js/token.js', 'homeContentArea', 'token'))
      .then(() => injectScript('/static/js/sideBar.js', 'homeContentArea', 'sideBar'))
        .then(() => updateStatus(1));
  },
  '/cards': () => {
    removeScript('online');
    removeScript('offline');
    removeScript('tournament');
    fetchMainContent('/cards', 'homeContentArea')
      .then(() => updateStatus(1));
  },
  '/offline': () => {
    fetchMainContent('/offline', 'homeContentArea')
      .then(() => injectScript('/static/js/offlinePong.js', 'homeContentArea', 'offline'))
      .then(() => updateStatus(2));
  },
  '/online': () => {
    fetchMainContent('/online', 'homeContentArea')
      .then(() => injectScript('/static/js/onlinePong.js', 'homeContentArea', 'online'))
      .then(() => updateStatus(2));
  },
  '/tournament': () => {
    fetchMainContent('/tournament', 'homeContentArea')
      .then(() => injectScript('/static/js/tournament.js', 'homeContentArea', 'tournament'))
      .then(() => updateStatus(2));
  },
  '/tourGame': () => {
    return fetchMainContent('/online', 'gameBox')
      .then(() => updateStatus(2));
  },
  '/login': () => {
    fetchMainContent("/login", 'mainContainer')
  },
  '/logout': () => {
    fetchMainContent("/logout", 'mainContainer')
      .then(() => updateStatus(0));
    removeScript('token');
    removeScript('offline')
    removeScript('online')
    removeScript('tournament');
  },
  '/profile': (uid) => {
    fetchMainContent("/profile/" + uid.toString() + "/" , 'profileContent')
      .then(() => updateStatus(1));
  },
  '/edit_profile': () => {
    editForm();
  }
}

function engine(pageUrl, param=null, addToHistory=true) {
  let promise = injections[pageUrl](param);
  if (addToHistory) {
    if (pageUrl == '/home') {
      pageUrl = '/cards';
    } else if (pageUrl == '/login') {
      pageUrl = '/logout';
    }
    history.pushState({ pageUrl: pageUrl }, '');
  }
  return promise;
}

window.addEventListener('popstate', (event) => {
  var state = event.state;
  if (state) {
    engine(state.pageUrl, false);
  }
});

window.addEventListener("unload", (e) => {
  updateStatus(0);
})

window.onbeforeunload = function (e) {
  updateStatus(0);

  var xhr = new XMLHttpRequest();
  xhr.open("GET", '/', false); // Synchronous request to the root URL
  xhr.send(null);

  return ''; // For some browsers
};
