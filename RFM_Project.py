import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

# Reading data from excel
df_ = pd.read_excel(".../online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()
df.head()
df.shape

# Descriptive statistics of the dataset
df.describe().T

# Statistical summary of non-numeric columns
df.describe(include=['O'])

# Are there any missing observations in the dataset? If yes, how many missing observations in each variable?
df.isnull().sum()

# Removing missing observations from the dataset
df.dropna(inplace=True)

# Unique number of products
#df["StockCode"].nunique()
df["Description"].nunique()

# How many of each product are there?
df["Description"].value_counts()

# The order of the five most ordered products from most to least
#df.groupby(["StockCode"]).agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()
#df.groupby(["StockCode", "Description"]).agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()
df.groupby(["Description"]).agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()

# Remove canceled transactions from the dataset
df = df[~df["Invoice"].str.contains("C", na=False)]

# Creating a variable named 'TotalPrice' that represents the total earnings per invoice
df["TotalPrice"] = df["Price"] * df["Quantity"]

df.head()

# Calculating RFM metrics

# Recency: The difference between the customer's last shopping date and the analysis date determined is taken.
# Frequency: If grouping according to customer id and counting the unique invoice value
# Monetary: Total money paid by each customer

df["InvoiceDate"].max()
today_date = dt.datetime(2011, 12, 11)

rfm = df.groupby(["Customer ID"]).agg({"InvoiceDate": lambda x: (today_date - x.max()).days,
                                        "Invoice": lambda y: y.nunique(),
                                        "TotalPrice": lambda z: z.sum()})

rfm.head()
rfm.columns = ["Recency", "Frequency", "Monetary"]

# Considering the descriptive statistical values of the data set,
# The monetary min value is 0. This line is removed because it is a non-monetized transaction.
rfm = rfm[rfm["Monetary"] > 0]

rfm.head()

# Generating RFM scores

rfm["Recency_Score"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1])

rfm["Frequency_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

rfm["Monetary_Score"] = pd.cut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5])

rfm["Monetary_Score"].value_counts()

rfm["RFM_SCORE"] = (rfm["Recency_Score"].astype(str) + rfm["Frequency_Score"].astype(str))


# Defining RFM scores as segment

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm.head(30)
rfm["Segment"] = rfm["RFM_SCORE"].replace(seg_map, regex=True)

rfm[["Segment", "Recency", "Frequency", "Monetary"]].groupby("Segment").agg(["mean", "count"])

# Creating a new dataframe
n_df = pd.DataFrame()

# Selecting the customer IDs of the "Loyal Customers" class
n_df["n_CustomerId"] = rfm[rfm["Segment"] == "loyal_customers"].index
n_df.head()

rfm[rfm["Segment"]== "loyal_customers"].head()
rfm[rfm["Segment"] == "champions"].head()
rfm[rfm["Segment"] == "cant_loose"].head()

# Getting the Excel output
n_df.to_excel("Loyal_Customers.xlsx")


"""
Cant loose: Although the recency averages of the segment are not very good, the frequency values are high, 
so this segment should be given importance.

Loyal customers: Both the frequency value and the recency value are at a good level compared to the average. Loyal customers should not be missed.


Champions: It is the segment with the best recency, frequency and monetary values. Transaction values; 
Recency, that is, the lowest temperature value. The highest frequency of purchases on average. 
In addition, its monetary value is the highest. This group is an important part of the company according to the pareto rule.

Actions to be taken: 
Handwritten messages and gifts can be sent to customers in addition to customized e-mails. 
Incentives can be offered. Discount on your next purchase. Giving rewards after a certain number of purchases. 
Return policies can be stretched. 
Loyalty program can be created. Gradual point systems can be made. 
VIP advantages can be provided. (Amazon Prime) 
Campaigns can be created through partnerships between companies 
Loyalty program can be gamified. With the game, a subscription service can be offered to the cant loose segment of the points and reward system . 
Creating exciting, entertaining and informative marketing content """