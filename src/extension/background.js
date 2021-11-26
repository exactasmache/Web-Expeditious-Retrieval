/** Data structures */
class ListNode {
  constructor(data) {
    this.data = data
    this.pointer = null
  }

  val = () => { return this.data; }

  next() { return this.pointer; }

  set_next(node) { this.pointer = node; }
}

class Cache {
  /**
   * This is a naive implementation of a cache. 
   * Since Extensions can store up to 5MB of data in localStorage
   * if we want to really scale it, we have to add an endpoint to 
   * the server and implement it there.
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

  has_and_update = (element) => {
    // TODO: In this case I had to put the element 
    // at the end of the list
    return this.hashes.has(element);
  }

  add = (element) => {
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
  }
}


/** Global variables */
let cache = new Cache(2);   //TODO: set to 10
const API_scheme = 'http'
const API_host = 'localhost:8888'
const API_url = `${API_scheme}://${API_host}`

/** Global Functions */
encode_utf8 = (s) => encodeURIComponent(s);

inputEntered = (text) => {
  const e_text = encodeURIComponent(text);
  const searchURL = `${API_url}/search/q=${e_text}`;
  
  chrome.tabs.create({url: searchURL})
  .catch( err => {
    console.log('ERROR', err);
  });
};


/** Event listeners */
chrome.omnibox.onInputEntered.addListener(inputEntered);

/* It receives the message from the content script and sends it
   to the server in order to add it to the index. */
chrome.runtime.onMessage.addListener(
  (request, sender, sendResponse) => {

    const url = sender.tab.url;
    console.log(sender);
    console.log(request);

    if (request.method === "store") {
      const md5 = request.hash;

      if (cache.has_and_update(md5))
        sendResponse({ message: "Text already cached." });

      data = {
        text: request.text,
        url: url
      }
      text = request.text
      fetch(`${API_url}/store`, {
        method: "POST",
        body: JSON.stringify(data),
        headers: {
          'Content-Type': 'application/json',
        }
      })
        .then(() => {
          cache.add(md5);
          console.log("Text saved.");
        })
        .catch((error) =>
          console.log("Could not store the text.", error));
    }
    sendResponse(true);
  }
);