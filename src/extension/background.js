/**
 * Custom data structures
 */
class ListNode {
  constructor(data) {
    this.data = data
    this.pointer= null
  }
  
  val = () => {
    return this.data;
  }
  
  next() {
    return this.pointer;
  }

  set_next(node) {
    this.pointer = node;
  }
}

class Cache {
  /**
   * This is a naive implementation of a cache. 
   * If we want to really scale we can add an endpoint to the
   * server and implement it there.
   * 
   * One problem with this implementation comes when we access
   * to a site that is cached in the middle of the list. In
   * that case we have to iterate over all the linked list to
   * find that element in order to put it at the end.
   * 
   * @param {*} maxSize 
   */

  constructor(maxSize) {
    this.head = null;
    this.tail = null;
    this.hashes = new Set();
    this.size = 0;
    this.maxSize = maxSize;
  }

  has = (element) => {
    return this.hashes.has(element);
  }

  add = (element) => {
    // TODO: In this case I had to put the element 
    // at the end of the list
    if (this.hashes.has(element))
      return true;                    
    
    const newNode = new ListNode(element);
    this.hashes.add(element);
    
    if (this.tail != null)
        this.tail.set_next(newNode);
    else
        this.head = newNode;

    this.tail = newNode;
    if (this.size < this.maxSize)
      this.size++;
    else {
      this.hashes.delete(this.head.val())
      this.head = this.head.next();
    }
    return false;
  }
}


/**
 *  Global variables 
 */
let cache = new Cache(2);

console.log("Background is running. ", cache.head);

/**
 * Global Functions 
 */
inputStarted = () => {
  console.log("We could suggest words.");
};


inputEntered = (text, disposition) => {
  console.log("We have to retrieve the results.");
  let newURL = `http://localhost:8888/${text}`;

  fetch(newURL)
    .then(response => {
        console.log(response);
    })
    .catch(error => {
        // handle the error
    });

  // chrome.tabs.create({ url: newURL });
};


/**
 * Events
 */
chrome.omnibox.onInputStarted.addListener(
  inputStarted,
);


chrome.omnibox.onInputEntered.addListener(
  inputEntered,
)


/* It receives the message from the content script and sends it
   to the server in order to add it to the index. */
chrome.runtime.onMessage.addListener(
  function (request, sender, sendResponse) {
    const url = sender.tab.url;
    if (request.method === "cached?") {
      const md5 = request.hash;
      sendResponse({ cached: cache.add(md5) });

    } else if (request.method === "store") {
      
    } else {
      sendResponse({});
    }
  }
);