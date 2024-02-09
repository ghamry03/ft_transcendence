/**
 * 
 * @param {*} pageUrl Example "/home"
 * @param {*} injectionPoint where to inject the fetched html example: "#mainContentArea" - has to be and id not class
 */
function fetchPage(pageUrl , injectionPoint) {
    fetch(pageUrl)
      .then(response => {
        return response.text();
      })
      .then(text => {
        var parser = new DOMParser();
        var doc = parser.parseFromString(text, "text/html").querySelector("body").innerHTML;
        
        document.querySelector(injectionPoint).innerHTML = doc;
        if (pageUrl == '/online') {
          var gamescript = document.createElement('script');
          gamescript.setAttribute('src','/static/js/canvas.js');
          document.querySelector(injectionPoint).appendChild(gamescript);
        }
        else if (pageUrl == '/offline') {
          var gamescript = document.createElement('script');
          gamescript.setAttribute('src','/static/js/offlinePong.js');
          document.querySelector(injectionPoint).appendChild(gamescript);
        }
      });
}