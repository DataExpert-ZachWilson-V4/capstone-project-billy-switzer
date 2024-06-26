# Real-time Stock Price Fluctuations Project

## Installation Instructions
### Prerequisites
Before cloning the repo, you will need:
- On your local machine:
	- Linux, MacOS, or Windows running [WSL](https://learn.microsoft.com/en-us/windows/wsl/install)
	- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
	- Inside WSL for Windows users; regular installation for Linux/Mac users
		- Python 3.10
		- Java Runtime Environment JRE (I'm running JRE 21.0.3)
		- [Spark 3.5](https://www.apache.org/dyn/closer.lua/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz)0
- In AWS
	- An Iceberg data lake running Trino
	- AWS Glue

### Environment Variables
For local variables, I recommend adding lines of the form ```export VARIABLE_NAME=variable_value``` to your ~/.bashrc file (or equivalent), then running ```source .bashrc```

| Variable name	| Description	| Location(s) |
|:------------|:-------------|:-------------|
| APCA_API_KEY_ID | Key ID for Alpaca.Markets API | .bashrc<br>airflow_settings.yaml |
| APCA_API_SECRET_KEY | Secret Key for Alpaca.Markets API | .bashrc<br>airflow_settings.yaml |
| POLYGON_API_KEY | Key ID for Polygon.io API | .bashrc<br>airflow_settings.yaml<br>.env  |
| POLYGON_ACCESS_KEY_ID | Secret Key for Polygon.io API | .bashrc<br>airflow_settings.yaml |
| DATA_ENGINEER_IO_WAREHOUSE | Trino catalog name | .bashrc |
| DATA_ENGINEER_IO_WAREHOUSE_CREDENTIAL | Trino credential | .bashrc |
| JAVA_HOME | Location of javac | .bashrc |
| AWS_SECRET_ACCESS_KEY | AWS Secret Access Key for Boto3 Client | .bashrc<br>.env |
| AWS_ACCESS_KEY_ID | AWS Access Key ID for Boto3 Client | .bashrc<br>.env |
| AIRFLOW__SECRETS__BACKEND | Location of Airflow Secrets | .env |
| AIRFLOW__SECRETS__BACKEND_KWARGS | Keyword arguments for airflow secrets: connections_prefix, variables_prefix, variables_prefix | .env |
| AWS_DEFAULT_REGION | Default AWS region | .env |
| AIRFLOW_CONN_AWS_DEFAULT | Connection prefix (aws://) | .env |
| AWS_S3_BUCKET_TABULAR | S3 bucket for Tabular/Iceberg/Trino installation | airflow_settings.yaml |
| TABULAR_CREDENTIAL | Tabular Credential | airflow_settings.yaml |
| CATALOG_NAME | Trino catalog name | airflow_settings.yaml |
| AWS_GLUE_REGION | Region for AWS Glue | airflow_settings.yaml |
| DATAEXPERT_AWS_ACCESS_KEY_ID | AWS Access Key ID for Boto3 Client | airflow_settings.yaml |
| DATAEXPERT_AWS_SECRET_ACCESS_KEY | AWS Secret Access Key for Boto3 Client | airflow_settings.yaml |

### Cloning and backfill
1. Clone this repo to a folder
2. Run the following two SQL scripts in your Trino SQL editor against the target Iceberg instance. Update schema name here and below as appropriate.
	- [005_billyswitzer.staging_daily_stock_price_cumulative-create_table.sql](sql/iceberg/005_billyswitzer.staging_daily_stock_price_cumulative-create_table.sql)
	- [010_billyswitzer.daily_stock_price_cumulative-create_table.sql](sql/iceberg/010_billyswitzer.daily_stock_price_cumulative-create_table.sql)
3. Uncomment the call to [load_staging_daily_stock_price_backfill.py](jobs/batch/load_staging_daily_stock_price_backfill.py) in [glue_job_runner.py](jobs/glue_job_runner.py) and execute the following in the command line: ```python3 -m jobs.glue_job_runner```
4. Comment out the function all above and uncomment the call to [load_stock_splits_backfill.py](jobs/batch/load_stock_splits_backfill.py) in glue_job_runner.py. Run glue_job_runner as above.
5. Run the following SQL scripts in the Trino SQL editor against the target Iceberg database:
	- [020_billyswitzer.daily_stock_price_cumulative-backfill.sql](sql/iceberg/020_billyswitzer.daily_stock_price_cumulative-backfill.sql)
	- [025_billyswitzer.daily_stock_split-create_table.sql](sql/iceberg/025_billyswitzer.daily_stock_split-create_table.sql)
	- [030_billyswitzer.dim_daily_stock_price-create_table.sql](sql/iceberg/030_billyswitzer.dim_daily_stock_price-create_table.sql)
	- [040_billyswitzer.current_day_stock_price-create_table.sql](sql/iceberg/040_billyswitzer.current_day_stock_price-create_table.sql)
6. Run [jobs/local/load_dim_ticker_details.py](jobs/local/load_dim_ticker_details.py) with spark-submit. This is likely to take 1-2 hours.
7. Open a new Terminal window and navigate to the parent folder of this repo. Follow the instructions [here](https://superset.apache.org/docs/installation/docker-compose/#installing-superset-locally-using-docker-compose) to clone Apache Superset to a new folder and run with Docker Compose. Superset will continue running in this Terminal window.
8. Import the [superset/dashboard_export.zip](superset/dashboard_export.zip) file to Superset and open the Dashboard.
9. In the main folder for this repo, type ```astro dev start```. Once in Airflow, wait for the load_daily_stock_price_dag to finish backfilling the tables, then run update_current_day_stock_price_microbatch_dag to populate the Superset dashboard in real time.



## Background and Motivation
I became interested in investing during my time as a Data Analyst with the North Carolina Department of the State Treasurer, working primarily with the Retirement Systems Division, which manages pension benefits for state and local government workers in the State of North Carolina. This interest was augmented after a conversation with my parents in which they revealed that their longtime financial advisor had often been more interested in his own commission than in their financial goals. I became determined at that point to learn to manage my own investments, which has proved to be an exciting and worthwhile hobby. While most of my investing has been and will likely continue to be in indexes as first proposed by [Jack Bogle](https://www.investopedia.com/terms/j/john_bogle.asp), my desire to explore real-time, near-real-time, and short-term investment opportunitites provided a natural choice for the capstone project for the DataExpert.io V4 bootcamp.

## Scope
There are practically as many opportunities to leverage real-time data in investing as there are investment instruments themselves. For this project I considered exploring equities (stocks), credit instruments (bonds, both commercial and government), Real Estate Investment Trusts, currency exchanges (both cryptocurrencies and currencies issued by governments), and deriviatives of the previous categories. Short-term changes in price and volume in any of these categories can suggest either buying opportunities, or the need for risk management to minimize losses. As most of my experience as an investor is in traditional equities, I decided to focus there for this initial implementation, and decided to further narrow scope to comparisons of real-time stock prices against historical ones. This project is a work in progress, and the current implementation should be considered a proof-of-concept.

## Target Audience
The target audience for this initial proof-of-concept are day traders or anyone who is looking for real-time suggestions of which stocks are above or below their historical price averages in order to identify potential buying or selling situations.

## Desired Insights
The initial implementation of the project seeks to answer the following questions:
1. What are the Top 50 stocks above/below their historical price?
	- Compared with most recent
		- Daily Close Price
		- 90 Day Average
		- 365 Day Average
	- Ordered by
		- Percent, both increasing and decreasing
2. How do the above measures vary by market capitalization?

## Output
The output of the project is an Apache Superset dashboard showing the percent difference of the current price with the previous day's closing price, the average of closing prices over the previous 90 days, and the average of closing prices over the previous year. The dashboard refreshes every 30 seconds, and is filterable by market cap.
![Dashboard](readme_links/dashboard_update_loop_ezgif.gif)

## Data sources
I considered the six data sources in the table for the project, and narrowed the list to Alpaca Markets and Polygon.io based on the support for streaming, the high API limit, and relatively low cost.

| Name           |  Monthly Price for Real-Time or Near-Real-Time    | API Limit | Notes | Real-Time Method                |
|:---------------|:--------------------------------------------------|:--------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------|
| [Alpaca Markets](https://alpaca.markets/) | $100.00| Unlimited websockets; 10k API requests per minute | | Websockets                      |
| [Alpha Vantage](https://www.alphavantage.co/)  | $250.00 | 1200 requests per minute | | Multiple API calls (microbatch) |
| [Finnhub.io](https://finnhub.io/)     | $130.00 | Unlimited websockets; 300 API requests per minute | | Websockets |
| [IEX Cloud](https://iexcloud.io/)      | $500.00 | | | Server Side Events              |
| [Polygon.io](https://polygon.io/)     | $200.00 | Unlimited | $30 for 15-minute-delayed data and basically all other functionality. Data accounts for splits (unlike Alpaca) and has more metadata than Alpaca | Websockets                      |
| [Yahoo Finance](https://finance.yahoo.com/)  | [N/A](https://algotrading101.com/learn/yahoo-finance-api-guide/) | | Streaming is not supported ||

I initially settled on Alpaca Markets as it is half the cost of Polygon.io for real-time data. After building the initial version of the project using Alpaca APIs for both historical and current data (in a microbatch), I discovered that the Alpaca data does not account for stock splits, nor does it provide an API to obtain this information. This is illustrated by an early version of the dashboard reporting NVIDIA (NVDA) being down 85% compared to the previous quarter, which is obviously incorrect:

![NVDA](readme_links/nvda_error_20240621.png)

Alpaca also fails to include the market cap dimension I had planned to use as a filter. After further research on Polygon.io, I discovered that they offer a $30/month plan which includes nearly all functionality, but provides real-time data with a 15-minute delay. Polygon.io does provide an API on stock splits, accounts for stock splits in the historical API, and also provides the ability to directly download historical CSV files from S3. Using Spark to connect to the files on Polygon.io's S3 server reduced the time to stage the previous day's data from 20 minutes to 2 when compared with using the historical API. Polygon.io also provides metadata on each company (Ticker Details), from which I pulled and categorized each asset's market cap.

Unfortunately I did discover during development that the stock split data from Polygon.io can arrive late. This occurred with STAF on 6/26/2024, as shown in the result set below:

![STAF](readme_links/staf_prices_missed_split.png)

I considered adding a filter to limit price differences displayed on the dashboard, but that filter increases the risk of hiding an actual result, such as this one from MLGO from 6/24/2024, where the difference between open and close price was nearly 300%.

![MLGO](readme_links/mlgo_legitimate_wide_spread.png)

A future enhancement for this project will handle late-arriving stock split data.

## Tech Stack
The tech stack for the project is as follows:
- [Starburst](https://www.starburst.io/) (Iceberg/Trino)
- [Airflow](https://airflow.apache.org/)
- [PySpark](https://spark.apache.org/docs/latest/api/python/index.html)
- Python [Requests](https://pypi.org/project/requests/) Library
- [Superset](https://superset.apache.org/)
- [AWS Glue](https://aws.amazon.com/glue/)

As part of the DataExpert.io course, students are provided access to an Iceberg data lake run by Starburst, as well as to an AWS Glue account for running Spark jobs, making these natural choices for the initial version of the project. Iceberg is a natural choice for storing batch data as tables are stored in Parquet format by default, utilizing run-length-encoding compression. I considered having the dashboard source hosted in Postgres, but as a proof-of-concept Iceberg is fully functional. Once the project incorporates actual streaming data I will likely move the dashboard source to Apache Druid to take advantage of its lower latency.

Airflow and PySpark are industry standards for pipeline orchestration and batch processing, respectively. After encountering difficulties linking a websocket both to Spark Streaming and Flink, I elected to move to a microbatch process to pull in data during the day. This process runs on a loop, updating each stock roughly every 4 minutes. As Spark does not provide much of an advantage with repeated API calls, and as it has a significant overhead in terms of memory and compute, I elected to use the Requests library in Python to handle the microbatch process. Spark does handle the final table update, but the API responses are stored in a list before briefly being converted to a pandas dataframe and finally to a PySpark dataframe for the final update.

I initially planned to use Tableau for the dashboard. Unfortunately in order to build a new Dashboard connected to a database (rather than a flat file) Tableau requires a [Creator](https://www.tableau.com/products/tableau#plans-pricing) license, which costs $900/year. For this reason I elected to use Apache Superset, which is open source.

## Metrics
The initial metrics chosen for the project are below, although only the three percentage metrics are shown on the dashboard at this time.

| Metric Name		| Metric Derivation		| Description	|
|:-------------	|:---------	|:-----------------	|
| m_price_change_last_day	| current_price - close_price_last_day	| Absolute price change compared with the previous day (USD)	|
| m_price_change_last_day_pct	| 100 * (current_price - close_price_last_day) / close_price_last_day	| Percentage price change compared with the previous day (USD)	|
| m_price_change_last_90_days	| current_price - close_price_avg_last_90_days	| Absolute price change compared with the average of the previous 90 days (USD)	|
| m_price_change_last_90_days_pct	| 100 * (current_price - close_price_avg_last_90_days) / close_price_avg_last_90_days	| Percentage price change compared with the average of the previous 90 days (USD)	|
| m_price_change_last_365_days	| current_price - close_price_avg_last_365_days	| Absolute price change compared with the average of the previous 365 days (USD)	|
| m_price_change_last_365_days_pct	| 100 * (current_price - close_price_avg_last_365_days) / close_price_avg_last_365_days	| Percentage price change compared with the average of the previous 365 days (USD)	|

The grain of each metric is stock_symbol. The initial Superset dashboard displays a chart showing the top 50 stocks sorted by the three percentage metrics both ascending and descending (two charts per metric). This charts will identify potential buying/selling/short opportunities for day traders in real time. A dashboard showing the changes in absolute price will be added at a later date.

## Data and Architecture
Daily stock data is loaded from the [Polygon.io Daily Aggregates Flat File](https://polygon.io/flat-files/stocks-day-aggs) into a staging table, combined with stock split data (from the [Polygon.io Reference Data API](https://polygon.io/docs/stocks/get_v3_reference_splits)), and merged into a cumulative table (daily_stock_price_cumulative) in Iceberg via a Spark job scheduled with Airflow. The daily_stock_price_cumulative table contains an array of the previous 365 days of price and volume data. This data is aggregated into a dimension table in Iceberg (dim_daily_stock_price) containing averages for comparison with real-time data. Finally, the dim_daily_stock_price is joined to the dim_ticker_details table (a one-time pull from the [Polygon.io Reference Data API](https://polygon.io/docs/stocks/get_v3_reference_tickers__ticker)) to pull in the market cap dimension and load to the current_day_stock_price table, which is updated by the microbatch process. The microbatch process pulls intraday data from the [Alpaca Markets Market Data API](https://docs.alpaca.markets/reference/stockbars-1). The architecture for the daily data flow is shown below.

![Architecture Diagram](readme_links/architecture_diagram_v2.png)

The daily_stock_price_cumulative was initially populated via a backfill from the Polygon.io Daily Aggregates Flat File for the previous year. Aggregating the data in a cumulative table provided a significant reduction both in cardinality and file size, as shown the table below.

| Table Name	| Row Count	| File Size (MB)	| Description	|
|:-------------	|:---------	|:-----------------	|:-----------------	|
| staging_daily_stock_price_backfill	| 2800315	| 71.3	| Staging table for backfill of previous year. Grain is ticker and snapshot_date.	|
| daily_stock_price_cumulative	| 12900	| 42.7	| Cumulative table containing a year of price data in an array. Grain is ticker. Values are for current partition.	|
| dim_daily_stock_price	| 12900	| 0.3	| Daily dimension table containing close price for previous day, previous quarter (average), and previous year (average). Grain is ticker. Values are for current partition.	|
| current_day_stock_price	| 12895	| 0.5	| dim_daily_stock_price for current day plus market cap and intraday prices and metrics. Grain is ticker.	|

The reduced cardinality, in particular, facilitates an efficient join between dim_daily_stock_price and dim_ticker_details, and the small footprint of current_day_stock_price facilitates rapid dashbaord updates. The aggregated grain along with the distributed capabilities of Spark will enable this model to handle additional markets and asset types in the future.

### Table Details

#### daily_stock_split
The daily_stock_split is a log of stock splits from the Polygon.io Reference API, and is used to apply split logic to data reported in the flat files. An example, on 6/10/2024, NVIDIA had a 10:1 stock split, with a split_from of 1 and a split_to of 10, meaning each share prior to 6/10 was worth 10 shares after 6/10. This table is joined with staging price data prior to merging into daily_stock_price_cumulative.

| Column		| Type		| Comment			|
|:-------------	|:---------	|:-----------------	|
| execution_date	| VARCHAR	| Date of the stock split		|
| split_from	| DOUBLE	| Share number before the split for conversion		|
| split_to	| DOUBLE	| Share number before the split for conversion		|
| ticker	| VARCHAR	| Stock Symbol		|
| as_of_date 	| DATE		| Most recent date imported (partition key)	|

##### Data Quality Checks
- Pipeline-level checks
	- Null values in array - this would indicate invalid split ratios

If the pipeline-level check fails, daily_stock_split is not updated and the pipeline fails.

#### daily_stock_price_cumulative
The daily_stock_price_cumulative table contains one row per ticker with a year's worth of price and volume data. Is the table on which each downstream table is built.

| Column		| Type		| Comment			|
|:-------------	|:---------	|:-----------------	|
| ticker	| VARCHAR	| Stock Symbol		|
| price_array 	| ARRAY(ROW(DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, BIGINT, DATE))	| Last 365 days of volume, open price, high price, low price, close price, transaction count, and snapshot date	|
| as_of_date 	| DATE		| Most recent date imported (partition key)	|

##### Data Quality Checks
- Pipeline-level checks
	- Null values in array - this would indicate invalid price/volume data
	- Total ticker count increases by no more than 1% day-to-day - this would likely indicate invalid ticker values

If either pipeline-level check fails, daily_stock_price_cumulative is not updated and the pipeline fails.

- Row-level checks
	- Volume > 0
	- All prices > 0

If any row-level check fails, that ticker's data is not loaded into daily_stock_price_cumulative, as a volume of 0 or any price of 0 are both invalid.
	
#### dim_daily_stock_price
The dim_daily_stock_price table contains one row per ticker with averages to be passed to the current_day_stock_price table.

| Column		| Type		| Comment			|
|:-------------	|:---------	|:-----------------	|
| ticker	| VARCHAR	| Stock Symbol		|
| close_price_last_day	| DOUBLE	| Previous day's closing price (i.e. - most recent value of price_array)	|
| close_price_avg_last_90_days	| DOUBLE	| Average of the previous 90 days of closing prices		|
| close_price_avg_last_365_days	| DOUBLE	| Average of the previous 365 days of closing prices		|
| as_of_date 	| DATE		| Most recent date imported (partition key)	|
	
##### Data Quality Checks
- Downstream from daily_stock_price_cumulative

#### dim_ticker_details
The dim_ticker_details table is (currently) a Type 0 SCD containing metadata on each ticker. This table also comes from the Polygon.io Reference Data API, but was loaded as an initial backfill rather than as part of the daily pipeline because of long load times. This table provides dimensional data for filtering dashboard results, although market_cap_description is currently the only column passed to the current_day_stock_price table and dashboard. Future enhancements will include regular updates to the table and combining catagories for the industry_description to group similar businesses together.

| Column		| Type		| Comment			|
|:-------------	|:---------	|:-----------------	|
| ticker	| VARCHAR	| Stock Symbol		|
| ticker_root	| VARCHAR	| The root of a specified ticker. For example, the root of BRK.A is BRK.		|
| company_name	| VARCHAR	| The company's registered name		|
| is_actively_traded	| BOOLEAN	| Whether or not the asset is actively traded. False means the asset has been delisted.		|
| currency_name	| VARCHAR	| The name of the currency that this asset is traded with (currently all USD).		|
| country	| VARCHAR	| Currently all US		|
| asset_type	| VARCHAR	| Currently either Stocks or OTC (over-the-counter) - stocks traded without being listed on an exchange		|
| market_cap	| DOUBLE	| Total dollar value of a company's outstanding shares of stock		|
| primary_exchange	| VARCHAR	| Exchange, e.g. the New York Stock Exchange (NYSE) or Nasdaq		|
| industry_description	| VARCHAR	| Description of a stock's industry/business		|
| weighted_shares_outstanding	| DOUBLE	| Total shares of a company's stock in the market		|
| market_cap_description	| VARCHAR	| Categories of market capitalization - > $200B is Mega Cap; $10B-$200B is Large Cap; $2B-$10B is Mid Cap; $250M-$2B is Small Cap; $0-$250M is Micro Cap. Stocks with a missing the market_cap are given a value of "Not Provided" 	|
| as_of_date 	| DATE		| Most recent date imported (partition key)	|

#### current_day_stock_price
The current_day_stock_price table is the source of the Superset Dashboard. It is truncated on weekdays at 10AM ET (market open) and replaced with the current partition of dim_daily_stock_price. It includes extra columns for the current stock price and last updated time, as well as the [Metrics](#metrics) defined above. These columns are populated by a microbatch job utilizing the Python Requests library and Spark.

| Column		| Type		| Comment			|
| -------------	| ---------	| -----------------	|
| ticker	| VARCHAR	| Stock Symbol		|
| close_price_last_day	| DOUBLE	| Previous day's closing price	|
| close_price_avg_last_90_days	| DOUBLE	| Average of the previous 90 days of closing prices		|
| close_price_avg_last_365_days	| DOUBLE	| Average of the previous 365 days of closing prices		|
| m_price_change_last_day	| DOUBLE	| Absolute price change compared with the previous day (USD)		|
| m_price_change_last_day_pct	| DOUBLE	| Percentage price change compared with the previous day (USD)		|
| m_price_change_last_90_days	| DOUBLE	| Absolute price change compared with the average of the previous 90 days (USD)		|
| m_price_change_last_90_days_pct	| DOUBLE	| Percentage price change compared with the average of the previous 90 days (USD)		|
| m_price_change_last_365_days	| DOUBLE	| Absolute price change compared with the average of the previous 365 days (USD)		|
| m_price_change_last_365_days_pct	| DOUBLE	| Percentage price change compared with the average of the previous 365 days (USD)		|
| current_price 	| DOUBLE		| Current price of the stock	|
| market_cap_description	| VARCHAR	| Description of market capitalization, e.g. - "Large Cap", "Mid Cap", etc.		|
| last_updated_datetime	| DATETIME	| Date/Time of last update in UTC	|


##### Data Quality Checks
- current_price > 0

### DAGs
#### Daily DAGs
Two DAGs update the system with daily and intraday stock data. The [load_daily_stock_price_dag](dags/etl/load_daily_stock_price_dag.py) loads the previous day's volume and price data, combines it with data on stock splits, and updates the daily_stock_price_cumulative table and the dim_daily_stock_price table for the previous day. The daily_stock_price_cumulative and daily_stock_split tables follow a write-audit-publish pattern. Other steps are added to ensure pipeline idempotency. This DAG runs daily, including weekends.

![load_daily_stock_price_dag](readme_links/load_daily_stock_price_dag_run.png)

The [update_current_day_stock_price_microbatch_dag](dags/etl/update_current_day_stock_price_microbatch_dag.py) runs on Monday-Friday, and initializes the current_day_stock_price table with data from dim_daily_stock_price, and runs a microbatch to pull data from the Alpaca Historical API throughout the day to update the table, thus updating the associated dashboard. Stocks update an average of once every 4 minutes. Additional logic to account for market holidays in the scheduling of this pipeline will be added at a later date.

![update_current_day_stock_price_microbatch_dag](readme_links/update_current_day_stock_price_microbatch_dag_run.png)

#### Backfills
The daily_stock_price_cumulative table and dim_ticker_details tables were both backfilled with data at the start of the project. The process to load the daily_stock_price_cumulative was similar to the daily load - data from 6/1/2023 onward was [pulled](jobs/batch/load_staging_daily_stock_price_backfill.py) from Polygon.io's Daily Aggregate Files on S3, merged with [stock split data](jobs/batch/load_stock_splits_backfill.py) from the Polygon.io Reference API (in the stock_splits_backfill table), then the last year's worth of data was [pulled](sql/iceberg/020_billyswitzer.daily_stock_price_cumulative-backfill.sql) for the initial partition of daily_stock_price_cumulative. 

I had originally intended for dim_ticker_details to be part of the load_daily_stock_price_dag, but since it required looping through API calls, this step took over an hour to complete. For this reason, I elected to [backfill](jobs/local/load_dim_ticker_details.py) this table once for the purposes of this proof-of-concept. Regular updates to this table will be considered in the future.

### Next Steps
The first North Star goal for this project is to move the intraday pipeline to real-time using either Spark Structured Streaming or Flink. However, in the current implementation, Spark and Iceberg are hosted on the DataExpert.io infrastructure, while Airflow and Superset are hosted locally on Docker. The first step will be to migrate the entire project to an AWS account which can host all the necessary resources for the project. Following the migration, adding a daily pipeline for late-arriving stock split data and aggregating the industry descriptions from dim_ticker_details are low effort projects with high impact. Streaming and migrating the current_day_stock_price data to Druid will likely follow. Finally, I will begin research on designing scenarios to train ML models to make predictions based on real-time data, and expand the scope of the project to asset classes other than stocks.