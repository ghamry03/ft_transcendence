function fetchMainContent(pageUrl, container=null) {
  return new Promise((resolve) => {
    fetch(pageUrl)
      .then(response => response.text())
      .then(data => {
        if (container != null) {
          var parser = new DOMParser();
          var doc = parser.parseFromString(data, "text/html").querySelector("body").innerHTML;
          document.getElementById(container).innerHTML = doc;
          resolve();  
        }
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
  fetch('/status/' + status.toString() + '/', {
  })
  // const data = new FormData();
  // data.append('status', status.toString());
  // navigator.sendBeacon('/status/', data);
  // console.log("how many times?");
}

function updateStatusUnload(e) {
  fetch('/status/0/', {
    keepalive: true
  });
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

// const injections = {
//   '/home': () => {
//     fetchMainContent('/home', 'mainContentArea')
//       .then(() => fetchMainContent('/topbar', 'topBar'))
//       .then(() => fetchMainContent('/cards', 'homeContentArea'))
//       .then(() => injectScript('/static/js/token.js', 'homeContentArea', 'token'))
//       .then(() => injectScript('/static/js/sideBar.js', 'homeContentArea', 'sideBar'))
//       .then(() => injectScript('/static/js/searchQuery.js', 'homeContentArea', 'sideBar'));
//   },
//   '/cards': () => {
//     removeScript('online');
//     removeScript('offline');
//     removeScript('tournament');
//     fetchMainContent('/cards', 'homeContentArea');
//   },
//   '/offline': () => {
//     fetchMainContent('/offline', 'homeContentArea')
//       .then(() => injectScript('/static/js/offlinePong.js', 'homeContentArea', 'offline'));
//   },
//   '/online': () => {
//     fetchMainContent('/online', 'homeContentArea')
//       .then(() => injectScript('/static/js/onlinePong.js', 'homeContentArea', 'online'));
//   },
//   '/tournament': () => {
//     fetchMainContent('/tournament', 'homeContentArea')
//       .then(() => injectScript('/static/js/tournament.js', 'homeContentArea', 'tournament'));
//   },
//   '/tourGame': () => {
//     return fetchMainContent('/online', 'gameBox');
//   },
//   '/login': () => {
//     fetchMainContent("/login", 'mainContainer');
//   },
//   '/logout': () => {
//     fetchMainContent("/logout", 'mainContainer');
//     removeScript('token');
//     removeScript('offline')
//     removeScript('online')
//     removeScript('tournament');
//   },
//   '/searchUsers': (url) => {
//     fetchMainContent(url, 'searchUsers');
//   }
// }

const injections = [
  {
    pattern: /^\/home$/,
    handler: () => {
      fetchMainContent('/home', 'mainContentArea')
        .then(() => fetchMainContent('/topbar', 'topBar'))
        .then(() => fetchMainContent('/cards', 'homeContentArea'))
        .then(() => injectScript('/static/js/token.js', 'homeContentArea', 'token'))
        .then(() => injectScript('/static/js/sideBar.js', 'homeContentArea', 'sideBar'))
        .then(() => updateStatus(1));
        window.addEventListener('unload', updateStatusUnload);
    }
  },
  {
    pattern: /^\/cards$/,
    handler: () => {
      removeScript('online');
      removeScript('offline');
      removeScript('tournament');
      fetchMainContent('/cards', 'homeContentArea')
      .then(() => updateStatus(1));
    }
  },
  {
    pattern: /^\/offline$/,
    handler: () => {
      fetchMainContent('/offline', 'homeContentArea')
        .then(() => injectScript('/static/js/offlinePong.js', 'homeContentArea', 'offline'))
      .then(() => updateStatus(2));
    }
  },
  {
    pattern: /^\/online$/,
    handler: () => {
      fetchMainContent('/online', 'homeContentArea')
        .then(() => injectScript('/static/js/onlinePong.js', 'homeContentArea', 'online'))
      .then(() => updateStatus(2));
    }
  },
  {
    pattern: /^\/tournament$/,
    handler: () => {
      fetchMainContent('/tournament', 'homeContentArea')
        .then(() => injectScript('/static/js/tournament.js', 'homeContentArea', 'tournament'))
      .then(() => updateStatus(2));
    }
  },
  {
    pattern: /^\/tourGame$/,
    handler: () => {
      return fetchMainContent('/online', 'gameBox')
      .then(() => updateStatus(2));
    }
  },
  {
    pattern: /^\/login$/,
    handler: () => {
      fetchMainContent("/login", 'mainContainer')
    }
  },
  {
    pattern: /^\/logout$/,
    handler: () => {
      fetchMainContent("/logout", 'mainContainer')
      .then(() => updateStatus(0));
      removeScript('token');
      removeScript('offline');
      removeScript('online');
      removeScript('tournament');
      window.removeEventListener('unload', updateStatusUnload);
    },
    // window.removeEventListener('unload')
  },
  {
    pattern: /^\/profile\/.*$/,
    handler: (url) => {
        fetchMainContent(url, 'profileContent')
        .then(() => updateStatus(1));
    }
  },
  {
    pattern: /^\/edit_profile\/.*$/,
    handler: (url) => {
        editform();
    }
  },
  {
    pattern: /^\/searchUsers\/.*$/,
    handler: (url) => {
      if (url != "/searchUsers/")
        fetchMainContent(url, 'searchUsers');
    }
  },
  {
    pattern: /^\/add\/.*$/,
    handler: (url) => {
      fetchMainContent(url);
    }
  },
  {
    pattern: /^\/accept\/.*$/,
    handler: (url) => {
      fetchMainContent(url);
    }
  },
  {
    pattern: /^\/reject\/.*$/,
    handler: (url) => {
      fetchMainContent(url);
    }
  }
];


function engine(pageUrl, addToHistory=true) {
  var promise;
  for (let route of injections) {
    if (route.pattern.test(pageUrl)) {
      promise = route.handler(pageUrl);
      break;
    }
  }
  // let promise = injections[pageUrl](pageUrl);
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

