function fetchMainContent(pageUrl, container=null) {
    return new Promise((resolve) => {
        fetch(pageUrl)
            .then(response => {
                if (!response.ok){
                    return response.json().then(body => {
                        throw new Error(body.error || 'Network response was not ok');
                    });
                }
                return response.text();
            })
            .then(data => {
                if (container != null) {
                    var parser = new DOMParser();
                    var doc = parser.parseFromString(data, "text/html").querySelector("body").innerHTML;
                    document.getElementById(container).innerHTML = doc;
                    resolve();
                }
            })
            .catch((error) => {
                showError(`Failed to load content. [${error.message}]`, 'Retry', () => {
                    fetchMainContent(pageUrl, container)
                });
            })
    });
}

function injectScript(src, container, id) {
    var scriptElement = document.createElement('script');
    scriptElement.src = src;
    scriptElement.id = id;
    document.getElementById(container).appendChild(scriptElement);
}

function updateStatus(status) {
    return new Promise((resolve) => {
        fetch('/status/' + status.toString() + '/', {
        })
        .then(() => resolve());
    });
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
            updateStatus(0)
                .then(() => fetchMainContent("/logout", 'mainContainer'));
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
    console.log('LEMEEEE IN');
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

function showError(errorMessage, buttonText, buttonOnClickFunction) {
    errorDiv = document.getElementById('main_error');
    errorText = document.getElementById('error_text');
    errorButton = document.getElementById('error_button');

    errorText.textContent = errorMessage;
    errorButton.textContent = buttonText;

    var myCollapse = new bootstrap.Collapse(errorDiv);


    myCollapse.show();

    errorButton.onclick = () => {
        buttonOnClickFunction();
        hideErrorMessage();
    }
}

function hideErrorMessage() {
    var errorDiv = document.getElementById('main_error');
    if (errorDiv.classList.contains('show')) {
        var myCollapse = new bootstrap.Collapse(errorDiv);
        myCollapse.hide();
    }
}
