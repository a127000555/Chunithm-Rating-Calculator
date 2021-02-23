# chunithm_crawler

![](https://chunithm-net-eng.com/mobile/images/logo.png)

A program to crawl all your score in chunithm-eng.net and calculate the your rating in BEST 30.

## Usage

* Your python version should >= 3.6, with pandas installed.

```
python try.py
Input your account name. (Aime) : <Your Accout Name>
Input your password : <Your password Name>
```

## Result

* Program will generate two csv. `output.csv` and `analysis.csv`

#### output.csv

* All records of your highest scores.

![image-20210223205113425](https://i.imgur.com/8mAEgGh.png)

> Example: My output.csv

#### analysis.csv

* Calculate your rating in each score and sort with rating. (You can use this csv to calculate your BEST 30) 
  * hidden: The level (譜面定数) of this chart.
  * rating: Your rating of this chart.
  * to_top: What rating you'll get if you get SSS on this chart.

![image-20210223205206038](https://i.imgur.com/sJIlNQq.png)

> Example: My analysis.csv

## Ending

Feel free to ask me to expand more features or update 譜面定数.