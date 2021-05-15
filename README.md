

# chunithm_crawler

![](https://chunithm-net-eng.com/mobile/images/logo.png)

A program to crawl all your score in chunithm-eng.net and calculate the your rating in BEST 30.

## Setup - Install prerequisites

```
pip install -r requirements.txt
```

* Or, you need to install pandas & requests.

## Login

* Support two login mechanism, login with Aime account or just give me your cookies in chunithm-net.

#### Login with aime

```
Use Aime account to analysis or chunithm website token? 
Use Aime type 'A', token type 'T': A
Input your account name. (Aime): <Your account name>
Input your password: <Your account password, the words you type will not show up>
```

#### Login with token

1. Login your chunithm-net.
2. Click **F12** (Open Dev Tools), find **Network** and press **F5** to reload the page.
3. Click `home/`  > `headers` > `request headers` > Copy `cookies`.
4. Run the script and type the cookies you copied.

```
python crawl.py
Use Aime account to analysis or chunithm website token? 
Use Aime type 'A', token type 'T': T
How to get token? Please refer to https://github.com/a127000555/chunithm_crawler
Now, enter your token / cookies: <The cookies you copied>
Maybe OK, try to analyze.
```

5. Boom! Finished!

![image-20210515203545565](https://i.imgur.com/0J5NNAH.png)

> The screenshot of correct steps.

* Issues:
  * If the script tells you `Your token is expired, please use new token or login with this script.` Please click **clear button** in browser. (![image-20210515204003167](https://i.imgur.com/n5FJMxH.png) in Google Chrome, ![image-20210515204034603](https://i.imgur.com/WBrHbZJ.png)in Firefox) Press **F5** to reload the chunithm-net and copy cookie again.

## Result

* Program will generate two csv. `output.csv` and `analysis.csv`

#### output.csv

* All records of your highest scores.

  ![image-20210515202110845](https://i.imgur.com/G6T4rEu.png)

> Example: My output.csv

#### analysis.csv

* Calculate your rating in each score and sort with rating. 
  * hidden: The level (譜面定数) of this chart.
  * rating: Your rating of this chart.
  * to_top: What rating you'll get if you get SSS on this chart.

![image-20210515202158572](https://i.imgur.com/CPS5PKd.png)

> Example: My analysis.csv

## Visualize

* A html file will generated if using the script successfully: `visualize.html`.
* This `html` has better looking to read and analysis your score & rating :).

* Note that you can only open this html when chunithm server is on.

<div style="display:flex">
    <img src="https://i.imgur.com/t3XRcLG.png" width=250px>
    <img src="https://i.imgur.com/dQMzI98.png" width=250px>
    <img src="https://i.imgur.com/HrEUvwi.png" width=250px>
</div>

> Example: My visualize.html

## Ending

Feel free to ask me for expanding more features or update 譜面定数.

## Author

Arvin Liu