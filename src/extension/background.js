/**
 * @author Marcelo Bianchetti <mbianchetti@dc.uba.ar>
 */

class CacheHandler {
  /**
   * Class to group all the functions developed in order to handle the 
   * cache, which is practicaly an Object with some functionalities 
   * inherited of a double linked list.
   * 
   * Example of accepted cache:
   * 
   * cache = {
   *   dl_list: {e1: {prev: null, next: e2}, e2: {prev: e1: next: null}}
   *   head: e1
   *   tail: e2
   *   size: 2
   *   maxSize: 10
   * }
   * We use this structure in order to be able to stringify and backup it
   * into the storage. Otherwise we could have a class.
   * Another option is to use indexDB, but I'm not really sure if we can
   * access it from the extension.
   */
  constructor() { }

  /**
   * Returns whether 'item' belongs to cache.
   * 
   * @param {Object} cache  - The cache in which to search.
   * @param {string} item   - The item to search into the cache.
   * @returns {boolean}     - False if 'item' does not belong to
   *                          the cache.
   */
  has = (cache, item) => cache.dl_list.hasOwnProperty(item);

  /**
   * Returns whether 'item' belongs to cache. 
   * If so, it updates the cache, realocating 'item' 
   * at the tail.
   * 
   * @param {Object} cache  - The cache in which to search.
   * @param {string} item   - The item to search into the cache.
   * @returns {boolean}     - False if 'item' does not belong to
   *                          the cache. True otherwise.
   */
  has_and_update = (cache, item) => {
    if (!cache.dl_list.hasOwnProperty(item))
      return false;

    // If 'item' is the head, we are done.
    let p_elem = cache.dl_list[item];
    if (!p_elem.next)
      return true;

    // Removes 'item' from the linked list.
    if (!p_elem.prev) {
      cache.dl_list[p_elem.next].prev = null;
      cache.head = p_elem.next;
    } else {
      cache.dl_list[p_elem.prev].next = p_elem.next;
    }
    cache.dl_list[p_elem.next].prev = p_elem.prev;

    // Appends 'item' at the end of the linked list
    let p_tail = cache.dl_list[cache.tail];
    p_elem.next = null;
    p_elem.prev = cache.tail;
    p_tail.next = item;
    cache.tail = item;
    return true;
  }

  /**
   * Adds the 'item' to the end of the cache. 
   * It assumes that the 'item' does not belong in the cache.
   * 
   * @param {Object} cache  - The cache in which to add the item.
   * @param {string} item   - The item to add to the cache.
   */
  add = (cache, item) => {
    // Initializes the node to add
    let newNode = {
      prev: null,
      next: null
    };

    // Adds the item as the tail
    if (cache.tail != null) {
      cache.dl_list[cache.tail].next = item;
      newNode.prev = cache.tail;
    } else {
      // Corner case: the cache is empty
      cache.head = item;
    }
    cache.tail = item;
    cache.dl_list[item] = newNode;

    if (cache.size < cache.maxSize) {
      cache.size++;
    } else {
      // Corner case: the cache reaches its limit
      // so it removes the head.
      let new_head = cache.dl_list[cache.head].next;
      delete cache.dl_list[cache.head];
      cache.head = new_head;
      cache.dl_list[cache.head].prev = null;
    }
  }
}


/** Global variables */
const STATUS_AVAILABLE = 'AVAILABLE';           // Available status
const API_scheme = 'http';                      // Server scheme.
const API_host = 'localhost:8888';              // Server host and port. 
const API_url = `${API_scheme}://${API_host}`;  // Server complete URL.
const API_newIndex = 'newindex';                // Endpoint for creating a new index.
const API_search = 'search';                    // Endpoint for searching words.

// Endpoint for checking server availability.
const API_serverAvailable = 'available';
/** 
 * Endpoint for checking index availability. 
 * If we want to stop sharing the indices, we could send the username. */
const API_indexAvailable = `${API_serverAvailable}/index`;

const cacheHandler = new CacheHandler();        // Structure to handle the cache.
const MAXSIZE = 10;                             // Max amount of elements allowed in the cache.
let cache;                                      // Cache.

/** Harcoded credentials for the pair test:test -> dGVzdDp0ZXN0 */
const user = 'test';
const pass = 'test';
const CREDENTIALS = `Basic ${btoa(`${user}:${pass}`)}`;

/**
 * Encodes text as an URI component.
 * 
 * @param {string} text - Text to encode.
 * @returns {string}      Encoded text.
 */
const encode_utf8 = (text) => encodeURIComponent(text);


/**
 * Sends a POST request to the server asking if 'text'
 * appears in the index. It renders the response in a
 * new tab.
 * 
 * @param {string} text - Text to search in the index.
 */
const inputEntered = (text) => {
  const e_text = encodeURIComponent(text);
  const searchURL = `${API_url}/${API_search}/q=${e_text}`;

  chrome.tabs.create({ url: searchURL })
    .catch(err => {
      console.log("Unable to show the results.", err);
    });
};

/**
 * Generates a new structure that represents an empty cache.
 * It is an Object with some functionalities inherited of a double 
 * linked list.
 * 
 * We use this plain structure in order to be able to stringify and 
 * backup it into the storage. Otherwise we could have a class.
 * Another option is to use indexDB, but I'm not really sure if we
 * can access it from the extension.
 * 
 * @constructor
 * @returns       An empty cache of MAXSIZE.
 */
const newCache = (maxSize) => {
  return {
    dl_list: {},            // Double linked list.
    head: null,             // First item.
    tail: null,             // Last item.
    size: 0,                // Amount of items.
    maxSize: maxSize        // Maximum amount of items allowed.
  };
};

/** 
 * Retrieves the cache from the storage.
 * This is executed each time the service_work wakes up. 
 */
const retrieveCacheFromStorage = chrome.storage.sync.get(['cache'])
  .then(items => {
    console.log("Cache retrieved:", items);
    if (items.cache != undefined)
      cache = JSON.parse(items.cache);
  })
  .catch(error => {
    console.log("Error retrieving cache:", error);
  });

/**
 * Saves the cache stringified in the storage with the key 'cache'.
 * 
 * @param {Promise} cache2save - Cache to save in the storage.
 */
async function backupCacheToStorage(cache2save) {
  chrome.storage.sync.set({ cache: JSON.stringify(cache2save) })
};

/**
 * Attempts to create a new index in the server.
 * 
 * @returns {Promise} 
 */
async function createIndex() {
  console.log("Creating a new index.");
  return fetch(`${API_url}/${API_newIndex}`, {
    method: "POST",
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': CREDENTIALS
    },
    body: JSON.stringify({}),
  });
}

/**
 * Attempts to create a new cache and to backup it in the storage.
 * The new cache is stored in the global variable 'cache'.
 * 
 * @returns {Promise}
 */
async function createCache() {
  console.log("Creating a new cache.");
  cache = newCache(MAXSIZE);
  return backupCacheToStorage(newCache(MAXSIZE));
}

/**
 * Attempts to initialize the cache. If the variable cache is not undefined,
 * it checks if the index exists and if so, it does not do anything else.
 * Otherwise, it creates the index and resets the cache.
 */
async function initializeCache() {

  if (cache != undefined) {
    /** If there is a local cache, it was retrieved from the storage, 
     * so we should check whether it is synchronized with the server,
     * instead of that (which requires some extra code) we asks for
     * the existence of any index, assuming it is synchronized. */
    let response = await fetch(`${API_url}/${API_indexAvailable}`, {
      method: "GET",
      credentials: 'include',
      headers: {
        'Authorization': CREDENTIALS
      }
    });
    let ret = await response.json();
    console.log(ret.message);
    if (ret.status == STATUS_AVAILABLE) return;
  }

  /** 
   * If the index is not available or if the cache is empty, 
   * we must reset the cache and possibly create a new index */
  try {
    await createIndex();
    await createCache();

  } catch (error) {
    console.log("Unable to create index or cache.", error);
  }
}

/** Event listeners */

/**
 * Creates a new index (if it does not exist) and a new cache. 
 * It is executed only when the extension is installed.
 */
chrome.runtime.onInstalled.addListener(() => {

  /** Checks if the index is available. It is a kind of ping */
  let server_available = fetch(
    `${API_url}/${API_serverAvailable}`, {
    method: "GET",
    credentials: 'include',
    headers: {
      'Authorization': CREDENTIALS
    }
  });

  server_available.then(initializeCache)
    .catch((error) => console.log("Unable to initialize cache.", error));

  server_available.catch((error) =>
    console.log("Unable to connect with the server.", error)
  );
});

/** Tries to store the text received into request.text */
async function storeRequest(data) {

  /** If cache is not loaded or if it does not exist yet. */
  if (cache == undefined) {
    try {
      await retrieveCacheFromStorage;
    } catch (err) {
      cache = newCache(MAXSIZE);
    }
  }

  /** Checks if cache has the hash, and resorts the cache in that case. */
  if (cacheHandler.has_and_update(cache, data.hash))
    return { message: "Text already cached." };

  /** Sends the text to the server. */
  const data2send = {
    text: data.text,
    url: data.url,
    title: data.title
  };
  try {
    await fetch(`${API_url}/store`, {
      method: "POST",
      body: JSON.stringify(data2send),
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': CREDENTIALS
      },
    });
  } catch (err) {
    console.log("Error sending the text to the server.", err);
    throw new Error(`Unable to store the text.`);
  }

  /** Updates and backups the cache. */
  cacheHandler.add(cache, data.hash);
  try {
    await backupCacheToStorage(cache);

  } catch (err) {
    console.log("Error when backuping the cache.", err);
    throw new Error(`Unable to update the cache.`);
  }

  console.log("new Cache:", cache);
  return { message: "Text stored and cache updated.", cache: cache };
}

/** 
 * Messages handler.
 * 
 * If request.method is 'store', then it must contain:
 *   @param {string} hash  - Hash of the URL + text.
 *   @param {string} text - Text to send to the server. 
 *  
 *   It receives the text from the content scripts and, if 
 *   it is not cached, sends it to the server in order to 
 *   add it to the index.
 */
chrome.runtime.onMessage.addListener(
  (request, sender, sendResponse) => {
    if (request.method != "store")
      return sendResponse(false);

    const hash = request.hash;
    if (cache != undefined && cacheHandler.has_and_update(cache, hash))
      return sendResponse({ message: "Text already cached. So we updated the cache." });

    let data = {
      hash: hash,
      text: request.text,
      url: sender.tab.url,
      title: sender.tab.title
    }

    /** Tries to send the text to the server and to update and backup the cache */
    storeRequest(data)
      .then(sendResponse)
      .catch((error) => sendResponse(`Unable to complete the process.\n ${error}`));

    /** Returns true to send a response asynchronously. */
    return true;
  });

/** 
 * Omnibox - onInputEntered - handler.
 * It listens to the 'WER' keyword (defined in the manifest).
 */
chrome.omnibox.onInputEntered.addListener(inputEntered);
