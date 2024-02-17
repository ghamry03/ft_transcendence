function fetchMainContent(pageUrl, container) {
  return new Promise((resolve) => {
    fetch(pageUrl)
      .then(response => response.text())
      .then(data => {
        var parser = new DOMParser();
        var doc = parser.parseFromString(data, "text/html").querySelector("body").innerHTML;
        document.getElementById(container).innerHTML = data;
        resolve();
      });
  });
}

function injectScript(script, container, id) {
  var scriptElement = document.createElement('script');
  scriptElement.src = script;
  scriptElement.id = id;
  document.getElementById(container).appendChild(scriptElement);
}

function removeScript(id) {
  script = document.getElementById(id);
  if (script) {
    console.log('removed the thing')
    script.remove();
  }
}

const injections = {
  '/home': () => {
    fetchMainContent('/home', 'mainContentArea')
      .then(() => fetchMainContent('/topbar', 'topBar'))
      .then(() => fetchMainContent('/cards', 'homeContentArea'))
      .then(() => injectScript('/static/js/token.js', 'homeContentArea', 'token'));
  },
  '/cards': () => {
    removeScript('online');
    removeScript('offline');
    fetchMainContent('/cards', 'homeContentArea');
  },
  '/offline': () => {
    fetchMainContent('/offline', 'homeContentArea')
      .then(() => injectScript('/static/js/offlinePong.js', 'homeContentArea', 'offline'));
  },
  '/online': () => {
    fetchMainContent('/online', 'homeContentArea')
      .then(() => injectScript('/static/js/canvas.js', 'homeContentArea', 'online'));
  },
  '/login': () => {
    fetchMainContent("/login", 'mainContainer');
  },
  '/logout': () => {
    fetchMainContent("/logout", 'mainContainer');
    clearInterval(pid);
    removeScript('token');
    removeScript('offline')
    removeScript('online')
  }
}

function engine(pageUrl, addToHistory=true) {
  injections[pageUrl]();
  if (addToHistory) {
    if (pageUrl == '/home') {
      pageUrl = '/cards';
    } else if (pageUrl == '/login') {
      pageUrl = '/logout';
    }
    history.pushState({ pageUrl: pageUrl }, '');
  }
}

window.addEventListener('popstate', (event) => {
  var state = event.state;
  if (state) {
    engine(state.pageUrl, false);
  }
});
