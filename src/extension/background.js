
class CacheHandler {
  /**
   * Object merged with a linked list.
   * Example of accepted cache.
   * 
   * cache = {
   *   dl_list: {e1: {prev: null, next: e2}, e2: {prev: e1: next: null}}
   *   head: e1
   *   tail: e2
   *   size: 2
   *   maxSize: 10
   * }
   */
  constructor() { }

  has = (cache, element) => cache.dl_list.hasOwnProperty(element);

  has_and_update = (cache, element) => {
    if (!cache.dl_list.hasOwnProperty(element))
      return false;

    // If element is the head, we are done.
    let p_elem = cache.dl_list[element];
    if (!p_elem.next)
      return true;

    // Removes the element from the linked list.
    if (!p_elem.prev) {
      cache.dl_list[p_elem.next].prev = null;
      cache.head = p_elem.next;
    } else {
      cache.dl_list[p_elem.prev].next = p_elem.next;
    }
    cache.dl_list[p_elem.next].prev = p_elem.prev;

    // Appends element at the end of the linked list
    let p_tail = cache.dl_list[cache.tail];
    p_elem.next = null;
    p_elem.prev = cache.tail;
    p_tail.next = element;
    cache.tail = element;
    return true;
  }

  add = (cache, value) => {
    let newNode = {
      prev: null,
      next: null
    };
    if (cache.tail != null) {
      cache.dl_list[cache.tail].next = value;
      newNode.prev = cache.tail;
    } else {
      cache.head = value;
    }
    cache.tail = value;
    cache.dl_list[value] = newNode;

    if (cache.size < cache.maxSize) {
      cache.size++;
    } else {
      let new_head = cache.dl_list[cache.head].next;
      cache.dl_list.delete(cache.head)
      cache.head = new_head;
      cache.dl_list[cache.head].prev = null;
    }
  }
}


/** Global variables */
const MAXSIZE = 10;
const API_scheme = 'http';
const API_host = 'localhost:8888';
const API_url = `${API_scheme}://${API_host}`;
const API_newIndex = 'newindex';
const API_search = 'search';
const cacheHandler = new CacheHandler();
let cache;

const encode_utf8 = (s) => encodeURIComponent(s);

const inputEntered = (text) => {
  const e_text = encodeURIComponent(text);
  const searchURL = `${API_url}/${API_search}/q=${e_text}`;

  chrome.tabs.create({ url: searchURL })
    .catch(err => {
      console.log('ERROR', err);
    });
};

const newCache = () => {
  return {
    dl_list: {},
    head: null,
    tail: null,
    size: 0,
    maxSize: MAXSIZE
  };
};

const initStorageCache = chrome.storage.sync.get(['cache'])
  .then(items => {
    cache = JSON.parse(items.cache);
  })
  .catch(error => {
    console.log("ERROR: retrieving the cache!", error);
  });

const saveStorageCache = (cache2save) =>
  chrome.storage.sync.set({ cache: JSON.stringify(cache2save) });

/** Event listeners */

/**
 * Creates a new index.
 * Creates a new cache.
 */
chrome.runtime.onInstalled.addListener(() => {
  fetch(`${API_url}/${API_newIndex}`, {
    method: "POST",
    body: JSON.stringify({}),
    headers: {
      'Content-Type': 'application/json',
    }
  })
    .then(() => {
      console.log("New index created.");
      saveStorageCache(newCache())
        .then(() => console.log("New cache backuped."));
    })
    .catch((error) => {
      console.log("Unable to create the index or cache.", error)
    });
});

/** Read a bit more abount async functions and refactor this function */
async function storeRequest(request, sender) {
  const md5 = request.hash;
  if (cache == undefined) {
    try {
      await initStorageCache;
    } catch (e) {
      console.log("ERROR", e);
      cache = newCache();
    }
  }
  if (cacheHandler.has_and_update(cache, md5))
    return { message: "Text already cached." };

  data = {
    text: request.text,
    url: sender.tab.url,
    title: sender.tab.title
  }
  text = request.text
  fetch(`${API_url}/store`, {
    method: "POST",
    body: JSON.stringify(data),
    headers: { 'Content-Type': 'application/json' }
  })
    .then(() => {
      cacheHandler.add(cache, md5);
      console.log("Hash added to the cache", cache);

      saveStorageCache(cache)
        .then(() => {
          console.log("Cache backuped")
          return { message: "Cache backuped" }
        });
    })
    .catch((error) => {
      console.log("Unable to store the text.", error)
      return { message: "Unable to store the text." }
    });
}

/** It receives the message from the content script and,
 * if it is not cached, sends it to the server in order 
 * to add it to the index. */
chrome.runtime.onMessage.addListener(
  (request, sender, sendResponse) => {
    if (request.method != "store")
      sendResponse(false);

    const md5 = request.hash;
    if (cache != undefined && cacheHandler.has_and_update(cache, md5))
      return sendResponse({ message: "Text already cached." });

    storeRequest(request, sender).then(
      (response) => {
        console.log("Response:", response);
        sendResponse(response);
      });
    return true; // return true to send a response asynchronously
  });


chrome.omnibox.onInputEntered.addListener(inputEntered);
