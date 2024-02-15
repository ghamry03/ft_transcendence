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

function isStillLoggedIn(isLoggedIn, expiryTime) {
    // TODO: check time
  if (isLoggedIn == "true")
    return true
  else
    return false
}

const injections = {
  '/home': () => {
    fetchMainContent('/home', 'mainContentArea')
      .then(() => fetchMainContent('/topbar', 'topBar'))
      .then(() => fetchMainContent('/cards', 'homeContentArea'));
    // injectScript('static/js/token.js', 'scripts', 'token');
  },
  '/cards': () => {
    fetchMainContent('/cards', 'homeContentArea');
    removeScript('online');
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
    // clearInterval(pid)
  },
}

function engine(pageUrl, isLoggedIn, expiryTime) {
  if (isStillLoggedIn(isLoggedIn, expiryTime)) {
    injections[pageUrl]();
  } else {
    injections['/login']();
  }
}

function getTopBar() {
  fetchMainContent("/topbar", 'topBar');
}
