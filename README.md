University-Results-scraping
===========================

Scraping results from Gitam University's public results page. Note: No authentication is needed.

#### PRE-REQ:
* For GNU/Linux type environment :
   sudo apt-get install nodejs

* For Windows environment :
   Open http://www.nodejs.org and Download the stuff !

#### How to Run :
Just open the repo and just execute the command 
> node app.js (or)
> nodejs app.js

Then open your browser and go to the localhost:3000 and your
analytics will be up and running.


#### TODO:
* Expand for all branches ( branches as in engineering )
* Making the node app deployable just by executing the app
* Support for other Db
* Use cache for storing intermediate results ( a memcache on top of the express server)
* Try and learn: Use redis workers to speed up download
