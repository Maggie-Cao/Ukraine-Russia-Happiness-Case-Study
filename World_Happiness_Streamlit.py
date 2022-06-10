#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 21:28:47 2022

@author: 21766
"""
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

st.set_page_config(layout="wide")

# Reading in and Cleaning the Data
happiness_2021 = pd.read_csv('world-happiness-report-2021.csv')
happiness_2005 = pd.read_csv('world-happiness-report.csv')
countries_dict = [country for country in happiness_2005
                ["Country name"].unique() if country in happiness_2021["Country name"].values]
happiness_2005 = happiness_2005.loc[happiness_2005["Country name"].isin(countries_dict)].reset_index(drop=True)
happiness_2021["year"] = 2021
happiness_2021.rename({"Ladder score":"Life Ladder",
                      "Healthy life expectancy":"Healthy life expectancy at birth",
                      "Logged GDP per capita":"Log GDP per capita"}, axis=1, inplace=True)
columns = list(happiness_2005.drop(["Positive affect", "Negative affect"], axis=1).columns) + ["Regional indicator"]
happiness = pd.concat([happiness_2005, happiness_2021[columns]])
happiness_2021.replace({'Swaziland': 'Eswatini'},inplace =True)
happiness.replace({'Swaziland': 'Eswatini'},inplace =True)
regional_dict = {k:v for k,v in zip(happiness_2021["Country name"], happiness_2021["Regional indicator"])}
regional_dict.update({'Congo':'Sub-Saharan Africa'})
happiness["Regional indicator"] = happiness["Country name"].replace(regional_dict)
happiness.drop(["Positive affect","Negative affect"], axis = 1, inplace = True)
happiness_2022 = pd.read_csv('2022.csv')
happiness_2022.columns = happiness_2022.columns.str.replace('Explained by: ', '')
happiness_2022_replace = {'Country': 'Country name','Happiness score':'Life Ladder',
                        'GDP per capita': 'Log GDP per capita',
                         'Healthy life expectancy':'Healthy life expectancy at birth'}
happiness_2022['year'] = 2022
happiness_2022['Country'] = happiness_2022['Country'].str.replace('*', '', regex = True)
happiness_2022.rename(happiness_2022_replace, axis = 1, inplace = True)
happiness_2022.replace({',': '.'}, inplace = True, regex =  True)
happiness_2022.replace({'Czechia':'Czech Republic','Eswatini. Kingdom of':'Eswatini'}, inplace = True)
happiness_2022[[col for col in happiness_2022.columns if col != 'Country name']]= happiness_2022.drop('Country name', axis = 1).astype(float)
happiness_2022.drop(index = [146], inplace = True, axis = 0)
happiness_2022 = happiness_2022[[col for col in happiness_2022.columns if col in happiness.columns] ]
happiness = pd.concat([happiness,happiness_2022])
happiness["Regional indicator"] = happiness["Country name"].replace(regional_dict)
happiness['year'] = happiness['year'].astype(int)
happiness = happiness.sort_values(['year','Country name']).reset_index(drop = True)
happiness_mean = happiness.drop('year', axis = 1).groupby(['Country name', 'Regional indicator']).mean().reset_index()

###################Functions for finding the nearest neighbor##############################3

def distance(pt1,pt2):
    return np.sqrt((np.sum(pt1 - pt2)**2))

def row_distance(row_1, row_2):
    return distance(np.array(row_1), np.array(row_2))


def distances(dataframe, example):
    data = dataframe.copy()
    dists = []
    attributes = data.drop(['Country name', 'Regional indicator'], axis = 1).copy()
    for i,row in attributes.iterrows():
        dist = row_distance(row, example.drop(['Country name', 'Regional indicator'],axis = 1))
        dists.append(dist)
    data['Distance'] = dists
    return data

def closest(data, example, k):
    return distances(data, example).sort_values('Distance').head(k+1)

def country_line(country_name, k=5, happiness_factor = 'Life Ladder'):
    country_df = closest(happiness_mean,happiness_mean.loc[happiness_mean['Country name']== country_name],k)
    country_plot = happiness.loc[happiness['Country name'].isin(country_df['Country name'])]
    line_plot = px.line(country_plot, x = 'year', y = happiness_factor, color = 'Country name', hover_name = 'Country name',
        hover_data = ['Regional indicator'], markers = True, title = f'{happiness_factor} of countries closest to {country_name}',
        color_discrete_sequence = px.colors.qualitative.Pastel)
    return line_plot
    
#######################Basic Information on Streaemlit######################################
st.sidebar.subheader('Table of contents')
st.sidebar.write('1. ','<a href=#case-study-on-russia-and-ukraine>Introduction</a>', unsafe_allow_html=True)
st.sidebar.write('2. ','<a href=#data-cleaning>Data cleaning</a>', unsafe_allow_html=True)
st.sidebar.write('3. ','<a href=#plots-and-graphs-for-the-general-world>Plots and Graphs for the General World</a>', unsafe_allow_html=True)
st.sidebar.write('4. ','<a href=#plots-and-graphs-for-ukraine-and-russia>Plots and Graphs for Ukraine and Russia</a>', unsafe_allow_html=True)
st.sidebar.write('5. ','<a href=#additional-resources>Additional resources</a>', unsafe_allow_html=True)
st.title('Case Study on Russia and Ukraine')
st.markdown('### Background Information')
st.markdown('It is 2022. A war is quietly brewing between 2 countries. Hidden conflict that spans over centuries is brought forth onto the battle field once again. It is the war between Ukraine and Russia.')
st.markdown('In some ways the war may be inevitable by looking at the history between Ukraine, Russia, and the west.')
st.markdown("During the second world war, Russia sided with the west on the allied after Germany broke the German - Soviet non aggression pact by attacking the Soviet Union. Although to the outside, the Allies were united and a very strong enemy to the Axis powers, they were not united on the inside. The Soviet Union never agreed much with the western countries, often arguing on what to do with captured countries, post - war actions, and where they would attack next. Tension was growing due to many different factors. I can say that one of the main differences that brought about conflict between the big 3 in the allies were the difference of their political and economic system. The western world consisted of countries that were capitalis, while the Soviet Union was a communist country. Due to the difference in their ideology, they never liked each other that much.")
st.markdown("More tension starts brewing afer 1945 when WWII ended, and started preparing another 'war' that was about to startle the world. The differences between the Soviet Union and the United States soon led them to have increased tension. The United States would then bring its conflict to invovlve many more countries")
st.markdown('Below is that data that is going to be used in this case study. It is a detailed representation of how happy the countries on in the world form 2005  - 2022. In this case study, I am going to be exploring the relationship between the happiness factors and events happening in Russia and Ukraine during the past decade.')
st.dataframe(happiness)

###############3######################## Data Cleaaning#####################################
st.header('Data Cleaning')
st.markdown('To start off, the most important thing to do is make sure that our data is fair and that it is a clear representation of what we are going to explore, which is the Russo - Ukrainian war. So for extra columns or rows that are unneeded, false, and unclear, it should either be changed or taken away from the data in order for us to analyze the data easier.')
st.markdown('Below, first take a look at our datasets that we are going to, first, join together then clean and use. This dataset ranges from 2005 to 2022. With this amount of data, it would be easier for us to analyze how happy or unhappy either the Ukrainians or the Russians are and how it is effected and affects world events.')

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('2005-2020')
    st.dataframe(happiness_2005.columns)

with col2:
    st.markdown('2021')
    st.dataframe(happiness_2021.columns)

with col3:
    st.markdown('2022')
    st.dataframe(happiness_2022.columns)
st.markdown('Here is only displays factors that are going to be analyzed in order for us to understand how the happiness factors may be a representation of worldly events happening in Russia and Ukraine both now and in the past. We want to analyze how the happiness may have changed throughout the years due to major events happening and, possibly, how the happiness factors may influence Ukraine and Russia. This may help us explain things regarding the Russo-Ukrainian war.')

#####################Merging of################################
st.markdown("Let's first ")

code = '''def hello():
     print("Hello, Streamlit!")'''
st.code(code, language='python')

##################################Graphs for the General World##############################
st.header('Plots and Graphs for the General World')
st.markdown('Now that we understand how our current dataset came to be what it is. We still may not have a complete idea on the data. The best way of understanding a data may be visual representations. Below are some visual representations of the happiness data with all the countries in it so you can play around and get familiar with the data before moving on.')
st.markdown("Here is a pie chart. A pie chart shows a part-to-whole relationship in a data. In this pie chart, you can pick any happiness factor for a region and compare the percentages between regions. The pie chart will add the statistics of each region and compare this region's statistics to the statistics of all the regions")
pie_chart_select = st.selectbox('Choose a happiness factor',  ['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption'])
fig_pie = px.pie(happiness, 'Regional indicator', pie_chart_select, height = 600, width = 1000, title = 'Happiness Scatter Plot for Countries Around the World')
st.plotly_chart(fig_pie)

if pie_chart_select == 'Life Ladder':
    st.markdown('When we have chosen the happiness factor of Life ladder, which is a general representation of happiness, we can see that Western Europe has the highest life ladder due to a percentage of 17.9%. It is closely followed by Sub-Saharan Africa(16.7%), then by Latin America and Carribean(15.9%), etc, with South Asia having the lowest in Life Ladder(General happiness indicator). ')


#######################################Scatter Plot#########################################

x_axis_scatter = st.selectbox('Choose a x axis happiness factor for this scatter plot',  ['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption', 'Regional indicator'])
y_axis_scatter = st.selectbox('Choose a y axis happiness factor for this scatter plot',  ['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption', 'Regional indicator'])
gdp_plot = px.scatter(happiness, x= x_axis_scatter, y= y_axis_scatter, color = 'Regional indicator',  hover_name = 'Country name', height = 600, width = 1000, title = 'Happiness Scatter Plot for Countries Around the World'
          )
st.plotly_chart(gdp_plot)

if x_axis_scatter == 'Generosity':
    st.markdown('dddd')
elif x_axis_scatter == 'Social support':
    st.markdown('dhhhuhuhd') 
else: 
    st.markdown('hi')
    
if y_axis_scatter == ('Life ladder'):
    st.markdown('dddd')


fig = px.scatter_3d(happiness, x='Life Ladder', y='Social support', z='year',color='Regional indicator', height = 1000, width = 1000)
x_axis_map = st.selectbox('Choose a happiness factor for this map', ['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption', 'Regional indicator'])
st.plotly_chart(fig)

####################################################Plots and Graphs for Ukraine and Russia##########################################################

st.header('Plots and Graphs for Ukraine and Russia')
st.markdown('dddddd')
######################## Closest country prediction graph###################################
Country = st.text_input('Choose a country', 'Ukraine')
k =int(st.text_input('Enter the number of neighbors closest to this country',5))
happiness_factor = st.selectbox('Select a happiness factor from the following list',  ['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption', 'Regional indicator'])
country_line_fig =  country_line(Country, k, happiness_factor)
st.plotly_chart(country_line_fig)

fig2 = px.choropleth(happiness,locations = "Country name",
                     locationmode = "country names",color = x_axis_map,
                     animation_frame = "year",
                   height = 600, width = 1000)
#fig.update_geos(fitbounds="locations", visible=False)
#fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig2)
x_axis_map_ru = st.selectbox('Choose a happiness factor below', ['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption', 'Regional indicator'])
if x_axis_map_ru == 'Generosity':
    st.markdown('dddd')
    range_color = [-0.5, 0.25]
elif x_axis_map_ru == 'Social support':
    st.markdown('dhhhuhuhd') 
else: 
    st.markdown('hi')



