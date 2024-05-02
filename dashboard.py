import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
from main import *
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# st.set_page_config(
#     page_title="Hello",
# )

@st.cache_data
def setup():
    # df = pd.read_csv("data/all_stations_data.csv")
    # return df

    df = pd.DataFrame(columns = ['Station', 'Date', 'Hour','LVLTYP1', 'LVLTYP2', 'ETIME', 'PRESS', 'PFLAG', 'GPH', 'ZFLAG', 'TEMP', 'TFLAG', 'RH', 'DPDP', 'WDIR', 'WSPD'])
    for station_name in station_names:
        temp_df = data_loading(station_name)
        temp_df['Station'] = station_name
        df = pd.concat([df,temp_df], ignore_index= True)
    df = preprocess(df)
    df = process_convention(df)
    df = add_new_features(df)
    return df

st.title("Dashboard for ISSR conditions")
df = setup()
alt_df = df
#df.to_csv("./data/all_stations_data.csv",index=False)


issr_df = df[(df['TEMP']<= -40) & (df['RH_ice'] >= 100)]
#fl_df = df[(issr_df['PRESS_ALT'] >=30000) & (df['PRESS_ALT'] <=43000) ]
fl_df = df
years = list(df['Year'].unique())
years.sort(reverse=True)
hours = ['00', '12']
# print(hours)
with st.sidebar:
    station = st.selectbox(
            "Select the station name",
            station_names,
        )


    year = st.selectbox(
            "Select the Year",
            years,
        )
    h = st.selectbox('select hour', hours)
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
obs = []
orig = []
for i in range(1,13):
    obs.append(issr_df[(issr_df['Station']==station) & (issr_df['Year']==year) & (issr_df['Month'].astype(int) == i)]['Date'].nunique())
    orig.append(df[(df['Station']==station) & (df['Year']==year) & (df['Month'].astype(int)==i)]['Date'].nunique())
month_df = pd.DataFrame(columns = ['Months', 'No of Days', 'No of obs'])
month_df['Months'] = months
month_df['No of Days'] = orig
month_df['No of ISSR'] = obs
month_df['No of No-ISSR'] = month_df['No of Days'] - month_df['No of ISSR']
month_df_long = month_df.melt(id_vars='Months', var_name='Value_Type', value_name='Days')
#print(month_df_long)
#st.bar_chart(data = month_df, x='Months', y=['No of Days', 'No of obs'])
# chart = alt.Chart(month_df_long, title = f"Monthly distribution of ISSR occurances in {year} in {station}").mark_bar().encode(
#         x=alt.X('Months:O', sort=months),
#         y= 'Days',
#         color = 'Value_Type',
#         #column = 'Value_Type',
#         tooltip=['Months', 'Value_Type', 'Days']
            
#     ).properties(
#     width=800,
#     height=400
# )

# st.altair_chart(chart)

# fig = px.histogram(month_df_long, x="Months", y="Days",
#              color='Value_Type', barmode='group',
#              #histfunc='count',
#              height=400, width=800)
fig = px.bar(month_df, x= "Months", y =["No of ISSR", "No of No-ISSR"], title="Monthly ISSR occurances", color_discrete_sequence = px.colors.qualitative.Pastel)
st.plotly_chart(fig)

filtered_data = df[(df['TEMP'] <= -40) & (df['RH_ice'] >= 100)]

# Convert the 'Date' column to datetime
filtered_data['Date'] = pd.to_datetime(filtered_data['Date'])

# Extract month and year from the 'Date' column
filtered_data['Month'] = filtered_data['Date'].dt.month
filtered_data['Year'] = filtered_data['Date'].dt.year

# Group by month and year, and count the number of unique days
unique_days_count = filtered_data.groupby(['Year', 'Month', 'Station'])['Date'].nunique().reset_index()
unique_days_count.rename(columns={"Date":"Days"}, inplace=True)
unique_days_count['Year-Month'] =  unique_days_count['Year'].astype(str) + ' - ' + unique_days_count['Month'].astype(str)

#print(unique_days_count)
fig_all = px.line(unique_days_count, x="Year-Month", y="Days", color='Station', markers=True, title="Monthly ISSR occurances")
st.plotly_chart(fig_all)
## Hourly chart
hourly_df = pd.DataFrame()
hours = list(df['Hour'].unique())
hourly_df['Hour'] = hours
issr_hours= []
nonissr_hours = []
for hour in hours:
    issr_hours.append(issr_df[(issr_df['Station']==station) & (issr_df['Year']==year) & (issr_df['Hour']==hour)]['Date'].nunique())
    nonissr_hours.append(df[(df['Station']==station) & (df['Year']==year) & (df['Hour']==hour)]['Date'].nunique() - issr_hours[-1])

hourly_df['No of ISSR'] = issr_hours
hourly_df['No of Non-ISSR'] = nonissr_hours

hourly_df_melted = hourly_df.melt(id_vars=['Hour'], var_name='ISSR Category', value_name='No of Days')
fig_h = px.pie(hourly_df_melted, values='No of Days', names='ISSR Category', hole=0.5, color='ISSR Category', title="Hourly ISSR occurances")
#fig_h = px.bar(hourly_df, x= "Hour", y =["No of ISSR", "No of Non-ISSR"], title="Hourly ISSR occurances", color_discrete_sequence = px.colors.qualitative.Pastel)

st.plotly_chart(fig_h)


st_fl_df = fl_df[(fl_df['Station']==station) &  
(fl_df['TEMP']<= -40) & (fl_df['RH_ice'] >= 100) & (fl_df['PRESS_ALT'] >=30000) & 
(fl_df['PRESS_ALT'] <=43000) & (fl_df['Hour']==h) & (fl_df['Year']== year)]
st_fl_df['bins'] = pd.cut(st_fl_df['PRESS_ALT'], bins=range(30000, int(st_fl_df['PRESS_ALT'].max()) + 1000, 1000), right=False, labels= list(range(30000, int(st_fl_df['PRESS_ALT'].max()), 1000)))
result = st_fl_df.groupby('bins')['Date'].nunique().reset_index(name='days_count')
#print(result)



depth_df = st_fl_df.groupby(['Date', 'Hour']).agg({'PRESS_ALT': ['max', 'min']}).reset_index()
depth_df['diff'] = depth_df[('PRESS_ALT','max')] - depth_df[('PRESS_ALT','min')]
fig2 = px.histogram(depth_df[depth_df[('Hour', '')]== h], x="diff", nbins=24)

def flying_region(fl_df):
    vd_df =  fl_df[  
(fl_df['TEMP']<= -40) & (fl_df['RH_ice'] >= 100) & (fl_df['PRESS_ALT'] >=30000) & 
(fl_df['PRESS_ALT'] <=43000)]
    vd_df['bins'] = pd.cut(vd_df['PRESS_ALT'], bins=range(30000, int(vd_df['PRESS_ALT'].max()) + 1000, 1000), right=False, labels= list(range(30000, int(vd_df['PRESS_ALT'].max()), 1000)))
    #print(vd_df.head())
    result = vd_df.groupby(['bins', "Station", "Year"])['Date'].nunique().reset_index()
    result.rename(columns= {"Date": "Days"}, inplace= True)
    result.rename(columns= {"bins": "Pressure Altitude"}, inplace= True)
    fig = px.bar(result, x= "Pressure Altitude",y= "Days", color= "Station", facet_col="Year",  barmode="group")
    return fig


st.plotly_chart(flying_region(fl_df))

def vertical_depth(fl_df):

    vd_df =  fl_df[  
(fl_df['TEMP']<= -40) & (fl_df['RH_ice'] >= 100) & (fl_df['PRESS_ALT'] >=30000) & 
(fl_df['PRESS_ALT'] <=43000)]
    vd_df = vd_df[(vd_df['Hour'] == '00') | (vd_df['Hour'] == '12')  ]
    vd_df['bins'] = pd.cut(vd_df['PRESS_ALT'], bins=range(30000, int(vd_df['PRESS_ALT'].max()) + 1000, 1000), right=False, labels= list(range(30000, int(vd_df['PRESS_ALT'].max()), 1000)))
    depth_df = vd_df.groupby(['Date', 'Hour', 'Station']).agg({'PRESS_ALT': ['max', 'min']}).reset_index()
    depth_df['Vertical Depth'] = depth_df[('PRESS_ALT','max')] - depth_df[('PRESS_ALT','min')]
    print(depth_df.head())
    fig = px.histogram(depth_df, x='Vertical Depth',
             color='Station',
             nbins = 24,
             #histfunc='count',
             #apattern_shape="Station",
             facet_col="Hour",
             #barmode="group",
            
             height=400, width=800)
    fig.update_traces(texttemplate='%{y}', textposition='outside')
    fig.update_layout(title='Histogram of ISSR Vertical Depth',
                  xaxis_title='Vertical Depth',
                  yaxis_title='Days', legend=dict(x=0, y=-0.1, orientation='h'))

    return fig

st.plotly_chart(vertical_depth(fl_df))

col01, col02 = st.columns(2)
chart_container1 = st.container()
tab1, tab2 = st.tabs(["ISSR days at FL30K - FL43K", "ISSR days with vertical depth"])

with tab1:
    st.bar_chart(result, x= "bins", y= "days_count", use_container_width=True)
    
with tab2:
    st.plotly_chart(fig2, use_container_width=True)
    #st.hist(depth_df[depth_df[('Hour', '')]== h], bins=24, color='skyblue', edgecolor='black')

#################



start_date = df['Date'].min()
end_date = df['Date'].max()

d= None
container2 = st.container()
col1, col2 = st.columns(2)
with col1:
    d = st.date_input('pick a date',end_date, min_value=start_date, max_value=end_date)
with col2:
    h_day = st.selectbox('Hour', ["00", "12"])

#with container:
col3, col4 = st.columns(2)
#col3.width = 500  # Adjust the width as needed
#col4.width = 500 
with container2:
    with col3:
        fig_day1= px.scatter(fl_df[(fl_df['Date']==pd.to_datetime(d))& (fl_df['Hour']==h_day) & (fl_df['PRESS_ALT'] <=43000)], x="RH_ice", y="PRESS_ALT", color = 'Station', color_discrete_sequence = px.colors.qualitative.Set1)
        fig_day1.add_vline(x=100, line_width=2, line_dash="dash", line_color="green")
        fig_day1.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
        st.plotly_chart(fig_day1, use_container_width=True)
    with col4:
        fig_day2= px.scatter(fl_df[(fl_df['Date']==pd.to_datetime(d))& (fl_df['Hour']==h_day) & (fl_df['PRESS_ALT'] <=43000)], x="TEMP", y="PRESS_ALT", color = 'Station', color_discrete_sequence = px.colors.qualitative.Set1)
        fig_day2.add_vline(x=-40, line_width=2, line_dash="dash", line_color="green")
        fig_day2.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
        st.plotly_chart(fig_day2, use_container_width=True)

# chart_container2 = st.container()
# col1, col2 = st.columns(2)
# with chart_container2:

#     if d:
#         sample = fl_df[(fl_df['Station']== station) &(fl_df['Date']==pd.to_datetime(d))& (fl_df['Hour']==h) & (fl_df['PRESS_ALT'] <=43000)]
#         with col1:
#             #st.scatter_chart(sample, x="RH_ice", y="PRESS_ALT")
#             base_chart = alt.Chart(sample).mark_circle().encode(
#                 x='RH_ice',
#                 y='PRESS_ALT'
#             )
            
#             vertical_line = alt.Chart(pd.DataFrame({'RH_ice': [100]})).mark_rule(color='red').encode(
#                 x='RH_ice:Q'
#             )
#             chart = (base_chart + vertical_line).properties(
#                 #title='Scatter Plot with Vertical Line'
#             )

#             st.altair_chart(chart, use_container_width=True)
#         with col2:

#             #st.scatter_chart(sample, x = "TEMP_F", y = "PRESS_ALT", color= "#ffaa00" )
#             base_chart = alt.Chart(sample).mark_circle(size= 70,color='orange').encode(
#                 x='TEMP',
#                 y='PRESS_ALT',
#                 tooltip=['TEMP', 'PRESS_ALT']
#             )
            
#             vertical_line = alt.Chart(pd.DataFrame({'TEMP': [-40]})).mark_rule(color='red').encode(
#                 x='TEMP:Q'
#             )
#             chart = (base_chart + vertical_line).properties(
#                 #title='Scatter Plot with Vertical Line'
#             )

#             st.altair_chart(chart, use_container_width=True)


################################
#print(depth_df.columns)
vertical_depth = depth_df[depth_df[('Hour', '')]== h]
vertical_depth.rename(columns={('Date', ''): 'Date', ('Hour', ''): 'Hour', ('PRESS_ALT', 'min'): 'min', ('PRESS_ALT', 'max'): 'max', ('diff', ''): 'diff'}, inplace=True)

fig3, ax = plt.subplots(figsize=(10, 6))
for _, row in vertical_depth.iterrows(): 
    ax.plot([row[('Date', '')], row[('Date', '')]], [row[('PRESS_ALT', 'min')], row[('PRESS_ALT', 'max')]], color='blue')

ax.set_xlabel('Date')
ax.set_ylabel('Altitude')
ax.set_title('Min and Max Altitude for Each Date')
plt.xticks(rotation=45) 
plt.grid(True)
plt.tight_layout()
#plt.show()
#st.pyplot(plt.gcf())
st.pyplot(fig3)
######
#------------------------------------#

# vertical_depth = pd.DataFrame({
#     'Date': pd.date_range(start='2024-01-01', end='2024-01-10'),
#     'PRESS_ALT_min': [10, 15, 20, 25, 30, 35, 40, 45, 50, 55],
#     'PRESS_ALT_max': [20, 25, 30, 35, 40, 45, 50, 55, 60, 65]
# })

# # Convert DataFrame to long format suitable for Altair
# vertical_depth_long = vertical_depth.melt(id_vars='Date', var_name='PRESS_ALT', value_name='Altitude')

# # Create Altair chart
# chart = alt.Chart(vertical_depth_long).mark_rule(size=10).encode(
#     x='Date:T',
#     y='Altitude:Q',
#     color=alt.Color('PRESS_ALT:N', scale=alt.Scale(scheme='category10'))
# ).properties(
#     width=600,
#     height=400,
#     title='Min and Max Altitude for Each Date'
# ).configure_axis(
#     labelAngle=45
# )

# # Display the chart using Streamlit
# st.altair_chart(chart, use_container_width=True)

#-------------------#

