import streamlit as st 
import plotly.express as px
import pandas as pd 
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstar!!!", page_icon=":bar_chart:", layout="wide")
st.title(" :bar_chart: Sample Superstore EDA")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# --- File Upload ---
f1 = st.file_uploader(":file_folder: Upload a file", type=["csv", "txt", "xlsx", "xls"])
if f1 is not None:
    df = pd.read_csv(f1, encoding="ISO-8859-1")
else:
    csv_path = r"D:\project\Sample - Superstore.csv"
    df = pd.read_csv(csv_path, encoding="ISO-8859-1")  # read the CSV if uploader not used

# --- Normalize column names ---
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

# --- Convert Order Date with dayfirst=True ---
df['order_date'] = pd.to_datetime(df['order_date'], dayfirst=True)

# --- Get min/max dates ---
start_date = df['order_date'].min()
end_date = df['order_date'].max()

col1, col2 = st.columns(2)
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", start_date))
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", end_date))

# --- Filter by date range ---
df = df[(df['order_date'] >= date1) & (df['order_date'] <= date2)].copy()

st.sidebar.header("Choose your filter:")

# Filter by Region
region = st.sidebar.multiselect("Pick your Region", df["region"].unique())
# Filter by State
state = st.sidebar.multiselect("Pick the State", df["state"].unique())
# Filter by City
city = st.sidebar.multiselect("Pick the City", df["city"].unique())

# --- Apply filters dynamically ---
filtered_df = df.copy()
if region:
    filtered_df = filtered_df[filtered_df["region"].isin(region)]
if state:
    filtered_df = filtered_df[filtered_df["state"].isin(state)]
if city:
    filtered_df = filtered_df[filtered_df["city"].isin(city)]

# --- Category Sales ---
category_df = filtered_df.groupby(by=["category"], as_index=False)["sales"].sum()

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(
        category_df,
        x="category",
        y="sales",
        text=['${:,.2f}'.format(x) for x in category_df["sales"]],
        template="seaborn"
    )
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values="sales", names="region", hole=0.5)
    fig.update_traces(text=filtered_df["region"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

cl1,cl2 =st.columns(2)
with cl1:
    with st.expander("Category_Viewdata"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data",data=csv,file_name = "Category.csv",mime="text/csv",
                           help='Click here to download the data as a CSV file')
        


with cl2:
    with st.expander("Region_Viewdata"):
        region_df = filtered_df.groupby(by="region", as_index=False)["sales"].sum()
        st.write(region_df.style.background_gradient(cmap="Oranges"))
        csv = region_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download Data",
            data=csv,
            file_name="Region.csv",
            mime="text/csv",
            help='Click here to download the data as a CSV file'
        )
filtered_df["month_year"] = filtered_df["order_date"].dt.to_period("M")

st.subheader("Time Series Analysis")

linechart = (
    filtered_df
    .groupby(filtered_df["month_year"].dt.strftime("%Y-%b"))["sales"]
    .sum()
    .reset_index()
)
linechart.columns = ["month_year", "sales"]

fig2 = px.line(
    linechart,
    x="month_year",
    y="sales",
    labels={"sales": "Amount", "month_year": "Month-Year"},
    height=500,
    width=1000,
    template="gridon"
)

st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of Timeseries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Data",
        data=csv,
        file_name="TimeSeries.csv",
        mime="text/csv"
    )

# Create a treemap based on Region, Category, Sub-Category
st.subheader("Hierarchical view of Sales using TreeMap")

fig3 = px.treemap(
    filtered_df,
    path=["region", "category", "sub-category"],  # lowercase column names
    values="sales",
    hover_data=["sales"],
    color="sub-category"
)

fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

chart1,chart2 = st.columns((2))
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtered_df,values ="sales",names ="segment",template ="plotly_dark")
    fig.update_traces(text = filtered_df["segment"],textposition="inside")
    st.plotly_chart(fig,use_container_width=True)

with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_df,values ="sales",names ="category",template ="gridon")
    fig.update_traces(text = filtered_df["category"],textposition="inside")
    st.plotly_chart(fig,use_container_width=True)

import plotly.figure_factory as ff
st.subheader("👉 Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample =df[0:5][["region","state","city","category","sales","profit","quantity"]]
    fig = ff.create_table(df_sample,colorscale="Cividis")
    st.plotly_chart(fig,use_container_width=True)
st.markdown("Month wise sub-Category Table")
# Month column from order_date
filtered_df["month"] = filtered_df["order_date"].dt.month_name()

# Pivot table: Sub-Category vs Month
sub_category_Year = pd.pivot_table(
    data=filtered_df,
    values="sales",
    index=["sub-category"],
    columns="month",
    aggfunc="sum"  # optional, good practice
)

st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

#Create the scatter plot
data1 = px.scatter(
    filtered_df,
    x="sales",
    y="profit",
    size="quantity"
)

data1.update_layout(
    title={
        "text": "Relationship between Sales and Profits using Scatter Plot",
        "font": {"size": 20}
    },
    xaxis={
        "title": {"text": "Sales", "font": {"size": 19}}
    },
    yaxis={
        "title": {"text": "Profit", "font": {"size": 19}}
    }
)

st.plotly_chart(data1, use_container_width=True)

with st.expander("View data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))

#download the original data set
csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Download Data',data = csv,file_name="Dta.csv",mime="text/csv")

                              




