function fetchMainContent(pageUrl, container) {
  fetch(pageUrl)
    .then(response => response.text())
    .then(data => {
      document.getElementById(container).innerHTML = data;
    });
}

function injectScript(script, container) {
  var scriptElement = document.createElement('script');
  scriptElement.src = script;
  document.getElementById(container).appendChild(scriptElement);
  // var s = document.createElement('script');
  // s.setAttribute('type', 'text/javascript');
  // s.value = 'alert(1)';
  // document.getElementById('scripts').appendChild(s);
}

function removeScript(script, container) {
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
    fetchMainContent('/home', 'mainContentArea');
    fetchMainContent('/topbar', 'topBar');
    injectScript('static/js/token.js', 'scripts');
  },
  '/game': () => {
    fetchMainContent('/game', 'mainContentArea');
  },
  '/login': () => {
    // fetchMainContent("/login", 'mainContentArea');
    fetchMainContent("/login", 'mainContainer');
    clearInterval(pid)
  },
}

function engine(pageUrl, isLoggedIn, expiryTime) {
  if (isStillLoggedIn(isLoggedIn, expiryTime)) {
    // fetchMainContent(pageUrl, 'mainContentArea');
    // fetchMainContent("/topbar", 'topBar');
    // document.addEventListener('DOMContentLoaded', function() {
    //   injectScript('/static/js/token.js', 'scripts')});
    // injectScript('/static/js/token.js', 'scripts');
    injections[pageUrl]();
  } else {
    fetchMainContent("/login", 'mainContainer');
    // document.getElementById('scripts').remove();
    clearInterval(pid)
  }
}

function getTopBar() {
  fetchMainContent("/topbar", 'topBar');
}
