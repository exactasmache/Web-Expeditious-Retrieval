# Web Expeditious Retrieval
The goal of this repository is to store an implementation of a Chrome extension that allows users to search through a shared navigation history. That is, the extension should be able to observe and record the sites visited by the users, and also allow users to perform a text-based search over the visited sites (i.e., searching over the textual contents of visited sites). In order to share the navigation history of multiple users, a backend service also needs to be implemented providing the means to perform text-based search over the unified navigation history.

## The extension
The Chrome extension is implemented in _Javascript_ using a __content\_script__ and a __service\_worker__. 
For the __content\_script__, which is instantiated for each visited tab, the visible text of visited sites is obtained using the _innerText_ over the main document. This text is processed in order to remove white-spaces, and the idea is to be able in a future to remove repeated words among other improvements.

The simplified text, together with the URL and the title of the tab is sent to the __service\_worker__. In order to reduce computational time we use an MD5 hash to search on the cache implemented in the background. 
A simple improvement could be to generate a two messages dialog, by firstly asking for the existence of the hash and then to tell the server to store it. But since the cache is too small, we prioritized the reduction of the amount of messages sent.

### The cache
In the background the cache is implemented with a new structure which is practically a _Javascript_ Object that allows removing and adding items in $\mathcal{O}(1)$ (on average, assuming enough buckets and that the hashing function disperses evenly, otherwise it requires $\mathcal{O}(n)$ in the worst case), using an internal double linked list. Here we have several things to take into account:

 - First at all it would be interesting to have a kind of callback in order to make some actions before the __service\_worker__ is about to get idle. The idea is to avoid '_backuping_' the cache for each modification. 

 - Another thing to take into account is how many times the __service\_worker__ is idle, because this structure is deserialized each time it wakes-up, which takes $\mathcal{O}(n)$ being $n$ the amount of hashes.

 - Maybe a more efficient implementation could consider using the IndexedDB. We did not try because we have never used it (and we thought we did not have enough time to learn it. We do not even know if we have access to those things from the extension).

## The Backend
Backend service is implemented in _Python_, using the given skeleton. The index is an instance of the class _Whoosh_, and we developed another class to handle it.
It allows having multiple sub-index, with the idea of being able to separate the users, for example.

## Authentication
We are using a quite simple authentication schema, for which it is enough just to have some credentials shared between the server and the client.

We assume we do not want to ask the client to get logged in before starting using the extension. In which case we should receive a pair username/password and return a kind of token, which should be stored in the client. Since we do not distinguish among clients we are assuming that step is already done, and we have the same token for every client. The __user:password__ that generates the token is __test:test__, and the token is the one stored as CREDENTIALS within the server.The user is asked to fill those fields only for the _search_.

We should use an external library such as auth0 or a more powerful framework, such as Flask or Django.

Note that we are not using HTTPS neither, so the security is almost non-existent.

## Tests
Some tests to verify the behavior of the server were implemented using unittest.
To run them, just run the following command

> python -m unittest

to run all of them, or the following replacing _path_ and _test_to_run.py_.

> python -m unittest tests/\<path\>/\<test\_to\_run.py\>

The time went out, but several tests should be added in order to assure the correctness of the application. In particular integration tests using all the endpoints provided by the API: _newindex_, _search_, ...

Regarding the frontend, we are installing _npm_ with the aim of using _Mocha_ and _Chai_ to test the different functionalities, but we have problems with _brew_ and the OS version, and solving them is taking us all day.

## Some assumptions and thoughts
 -  If the page has some time-dependent value or things like that, we can have one URL for several texts. Thus, since the relation between the URL and the _innerText_ is not 1:1, we are not able to use the URL instead of a hash. Anyway, since we are not storing the text in the index, we are not able to differentiate contents for the same URL.

 - We assumed the cache must be implemented in the frontend without using any external API. 

 - We assumed the _chrome.storage_ is shared among different users, because we were not able to find documentation.
If this is not truth, and we want the cache to be shared among them, we should find another way.

 - As mentioned, we could improve the extension by reducing the text sent both in the search and in the store endpoints. For the last one it is necessary to study the index deeper. We observed that it removes the punctuation marks among other things, so we could omit to send them.

## Installation
The server requires python3.9 or earlier because it uses __\_\_file\_\___ to retrieve the abstract path to the script in order to create the index folder.

To install the server dependencies go to the _./src_ folder and run:
 >  pip install -r requirements.txt

If you prefer you can previously generate a virtual environment:
 > virtualenv -p python venv
 > . venv/bin/activate

To start the server just execute the script _wer.py_ located in _./src/server_.
> python server/wer.py

Running the script will start a service listening to HTTP requests at http://localhost:8888.

To load the extension go to chrome://extensions, enable __Developer mode__, click __Load unpacked__ and select the __src/extension__ folder.

