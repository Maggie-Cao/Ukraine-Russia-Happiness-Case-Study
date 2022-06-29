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
from PIL import Image
from streamlit_option_menu import option_menu


st.set_page_config(layout="wide")

# Reading in and Cleaning the Data
happiness_2021 = pd.read_csv('DataScience/world-happiness-report-2021.csv')
happiness_2005 = pd.read_csv('world-happiness-report.csv')
countries_dict = [country for country in happiness_2005
                ["Country name"].unique() if country in happiness_2021["Country name"].values]
#Countries dict makes a list of countries in the 2005 dataset that is also present in the 2021 dataset cause they are not the same. Some coutnries in the 2005-2020 datset are not in the 2021 dataset.
happiness_2005 = happiness_2005.loc[happiness_2005["Country name"].isin(countries_dict)].reset_index(drop=True)
# It takes out the countries that are in both the 2005 and 2021 dataset out of the 2005 dataset.
happiness_2021["year"] = 2021 #adds a new column to the 2021 datsaset called year that has all the inputs be the year of 2021;
happiness_2021.rename({"Ladder score":"Life Ladder",
                      "Healthy life expectancy":"Healthy life expectancy at birth",
                      "Logged GDP per capita":"Log GDP per capita"}, axis=1, inplace=True)#Rename the columns of the 2021 dataset so that the column names of the 2 datasets are the same.
columns = list(happiness_2005.drop(["Positive affect", "Negative affect"], axis=1).columns) + ["Regional indicator"] # You are making a list of the names of the columns that you want and dropping the names of columns that you don't want from the list(the rest). We add column called regional indicator to the 2005 dataset because it doesn't have one.

happiness = pd.concat([happiness_2005, happiness_2021[columns]])#combining the 2005 and 2021 but only combining the columns that we chose in the line previously(meaning we don't take the columns that is only present in 2021 and aren't in 2005. Also take the regional indicator column since the 2005 one doesn't have it.)
happiness_2021.replace({'Swaziland': 'Eswatini'},inplace =True)# replace the name of swaziland to eswatini because the name of the country changed from the 2021 dataset.
happiness.replace({'Swaziland': 'Eswatini'},inplace =True)#replace the name of swaziland to eswatini because the name of the country changed from the combined dataset of 2005 and 2021.
regional_dict = {k:v for k,v in zip(happiness_2021["Country name"], happiness_2021["Regional indicator"])} #here we are using dictionary comprehension, to make a list/dictionary that pulls the names and regional indicator of the countries in the 2021 dataset. 
regional_dict.update({'Congo':'Sub-Saharan Africa'})# adding the regional indicator of congo to sub saharan africa
happiness["Regional indicator"] = happiness["Country name"].replace(regional_dict)# applying the regional indicator that we pulled out of 2021 and applying it to the 2005 and 2021 dataset.
happiness.drop(["Positive affect","Negative affect"], axis = 1, inplace = True)#actually drop the positive affect and negative affect from the happiness dataset.
happiness_2022 = pd.read_csv('2022.csv')#reading in the 2022 happiness dataset.
happiness_2022.columns = happiness_2022.columns.str.replace('Explained by: ', '')#removed all the column names that has explained by in front of it.
happiness_2022_replace = {'Country': 'Country name','Happiness score':'Life Ladder',
                        'GDP per capita': 'Log GDP per capita',
                         'Healthy life expectancy':'Healthy life expectancy at birth'}#making a dictionary of column names that we want to change in order for the column names to be the same with the happiness dataset(merged dataset).
happiness_2022['year'] = 2022# adding the year column to the 2022 dataset and setting all the values to 2022.
happiness_2022['Country'] = happiness_2022['Country'].str.replace('*', '', regex = True)#take out the * in some of the country names(cleaning the data).
happiness_2022.rename(happiness_2022_replace, axis = 1, inplace = True)#renaming the columns so that the column names are the same throughout all the dataset.
happiness_2022.replace({',': '.'}, inplace = True, regex =  True)#in the statistics, ',' are used instead of '.', changing commas to dots.
happiness_2022.replace({'Czechia':'Czech Republic','Eswatini. Kingdom of':'Eswatini'}, inplace = True)# changing names of countries so that they are the same/consistent with the other datasets.
happiness_2022[[col for col in happiness_2022.columns if col != 'Country name']]= happiness_2022.drop('Country name', axis = 1).astype(float) #exclude the country names(country names cannot be converted to a float) and converting the statistics to floats.
happiness_2022.drop(index = [146], inplace = True, axis = 0)#drop the last row since the last row was corrupted and empty.
happiness_2022 = happiness_2022[[col for col in happiness_2022.columns if col in happiness.columns] ]#taking only the columns that are in the merged dataset.
happiness = pd.concat([happiness,happiness_2022])#merging the 2022 dataset to the perviously merged dataset.
happiness["Regional indicator"] = happiness["Country name"].replace(regional_dict)#applying the reigonal indicator to the merged happiness dataset(this is for the 2022 dataset that got merged))
happiness['year'] = happiness['year'].astype(int)#converting the year to int.
happiness = happiness.sort_values(['year','Country name']).reset_index(drop = True)#sort the year and country names. First view the year and all the countries in that year(alphabetical order) and then going to the next year. this is necessary for using the animation frames in the visual representation/plotly.
happiness_mean = happiness.drop('year', axis = 1).groupby(['Country name', 'Regional indicator']).mean().reset_index()# taking the mean values of all the countries so that it can be used in the k-neighbors function.




######Original Uncleaned Datasets######
happiness_2021_1 = pd.read_csv('world-happiness-report-2021.csv')
happiness_2005_1 = pd.read_csv('world-happiness-report.csv')
happiness_2022_1 = pd.read_csv('2022.csv')
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
    
#######################Basic Information on Streamlit######################################
# =============================================================================
# st.sidebar.subheader('Table of contents')
# st.sidebar.write('1. ','<a href=#case-study-on-russia-and-ukraine>Introduction</a>', unsafe_allow_html=True)
# st.sidebar.write('2. ','<a href=#data-cleaning>Data cleaning</a>', unsafe_allow_html=True)
# st.sidebar.write('3. ','<a href=#background-information>Background Information</a>', unsafe_allow_html=True)
# st.sidebar.write('4. ','<a href=#plots-and-graphs-for-the-general-world>Plots and Graphs for the General World</a>', unsafe_allow_html=True)
# st.sidebar.write('5. ','<a href=#plots-and-graphs-for-ukraine-and-russia>Plots and Graphs for Ukraine and Russia</a>', unsafe_allow_html=True)
# st.sidebar.write('6. ','<a href=#additional-resources>Additional resources</a>', unsafe_allow_html=True)
# =============================================================================
#sidebar menu
with st.sidebar: 
	selected = option_menu(
		menu_title = 'Navigation Pane',
		options = ['Introduction', 'Background Information', 'Data Cleaning', 
		'Plots and Graphs for the General World','Data Analysis', 'Conclusion'],
		menu_icon = 'bookmark-heart',
		icons = ['bookmark-check', 'book', 'box', 'bar-chart','graph-up', 
		'check2-circle','blockquote-left'],
		default_index = 0,
		)
if  selected == 'Introduction':
    
    st.title('Case Study on Russia and Ukraine')
    st.markdown('### Introduction')
    image_1 = Image.open('642d9048-b37f-11e3-bc21-00144feabdc0.jpg')
    st.image(image_1, caption= "Artistic Depiction of Putin's attempt in Russia")
    st.markdown('It is 2022. A war is quietly brewing between 2 countries. Hidden conflict that spans over centuries is brought forth onto the battle field once again. It is the war between Ukraine and Russia.')
    st.markdown('In some ways the war may be inevitable by looking at the history between Ukraine, Russia, and the west.')
    st.markdown("During the second world war, Russia sided with the west on the allied after Germany broke the German - Soviet non aggression pact by attacking the Soviet Union. Although to the outside, the Allies were united and a very strong enemy to the Axis powers, they were not united on the inside. The Soviet Union never agreed much with the western countries, often arguing on what to do with captured countries, post - war actions, and where they would attack next. Tension was growing due to many different factors. I can say that one of the main differences that brought about conflict between the big 3 in the allies were the difference of their political and economic system. The western world consisted of countries that were capitalis, while the Soviet Union was a communist country. Due to the difference in their ideology, they never liked each other that much.")
    st.markdown("More tension starts brewing afer 1945 when WWII ended, and started preparing another 'war' that was about to startle the world. The differences between the Soviet Union and the United States soon led them to have increased tension. The United States would then bring its conflict to invovlve many more countries")
    st.markdown('Below is that data that is going to be used in this case study. It is a detailed representation of how happy the countries on in the world form 2005  - 2022. In this case study, I am going to be exploring the relationship between the happiness factors and events happening in Russia and Ukraine during the past decade.')
    data_select = st.selectbox('Choose a dataframe to view',  ['World Happiness Dataset(cleaned)', 'World Happiness Dataset 2005-2020', 'World Happiness Dataset 2021', 'World Happiness Dataset 2022'])
    
    if data_select == 'World Happiness Dataset(cleaned)':
        st.dataframe(happiness)
    if data_select == 'World Happiness Dataset 2005-2020':
        st.dataframe(happiness_2005_1)
    if data_select == 'World Happiness Dataset 2021':
        st.dataframe(happiness_2021_1)
    if data_select == 'World Happiness Dataset 2022':
        st.dataframe == st.dataframe(happiness_2022_1)
    
#############################################################Background information#################################################################
if selected == 'Background Information':
    st.title("Background Information")
    
    st.markdown("An imminent threat. An upcoming terror. A approaching storm of troops at the border of Ukraine. On Febuary 23rd 2022, the Biden administration had made the affirmation in which Putin has decided upon Ukraine. Certainly, the very next day, the invasion of Ukraine began. ")
    image_2 = Image.open('Untitled-31.jpg')
    st.image(image_2, caption= "Picture taken of Zelensky and Putin",  use_column_width = 'auto')
    st.markdown("Understanding the current status of Russia and Ukraine is a key to understanding this case study on how the Ukrainian conflict influeced the happiness of the people in both countries.")
    st.subheader("What is the purpose of the war in Ukraine?")
    st.markdown("BBC Bitesize says that Putins' original goal was to try to overrun the Ukraine government and ending, for good, Ukraine's attempt to join NATO. He wasn't able to achieve this. He now is turning his ambition towards Ukriane's East and South. We are going to first look at how Putin, the president of Russia looks at the issue. It is important to approach a problem from many viewpoints. Putin tells the Russian people that the attack on Ukraine is to 'demilitarise and de-Nazify Ukraine'. He also claims that he wants to free the Ukrainian people from the Ukrainian government's oppression and genocide. No substantial amount of evidence supports this. On the contrary, Zelensky seems to be very popular with the Ukrainian people. Putin also tells the public that he has no choice to invade the country since he feels that Ukraine is an imminent threat to Russia.")
    st.markdown("Putin pulled out of Kyiv, a month into the invasion. He then tries to invade Donbas. 'Putin needs a victory,' said Andrei Kortunov, head of the Russian International Affairs Council. 'At least he needs something he can present to his constituency at home as a victory'.")
    st.markdown("In what way does Putins see Ukraine? Well, after the Soviet Union collapsed in 1991, Ukraine gained its independence. Putin believes Ukrainan and Russia peopel are actually of one people, and he doesn't accept that Ukraine is a sovereign state. He beleives that Ukraine is just a sort of 'anti-Russia project'. He accuses the countries in NATO, without proof, that they are trying to threaten 'our historic future as a nation'. Also, they accuse NATO on trying to wage proxy war on Crimea according to BBC Bitesize.")
    st.markdown("So far we have mentioned NATO many times, but what is Putin's problem with NATO?")
    st.markdown("This has to start way back to the time that WWII had ended. In 1949, NATO was created as the North Atlantic Treaty Organization, a military group that seeked defence and security as a whole group: trying to prevent something like WWII from happening again. Since then, NATO has been spreading its influence throughout Europe and also North America. Currently 30 countries had already joined NATO. If we observe the world map below , we can see that NATO's expansion has reached Russia, with Ukraine just in between NATO's influence and RUssia. ")
    image_3 = Image.open('/Users/Maggie/Desktop/Maggie - school /DataScience/NATO Influence.png')
    st.image(image_3, caption = "This image depicts NATO's influence in Europe till 2016.",width = 800)
    st.markdown("Russia in some ways is scared and afraid of NATO's influence. Many of the world powers like UK and US are in it, and militarily speaking, could pose a huge threat to Russia if it is standing right next to Russia. If Ukraine is taken and is part of NATO, there will be 'wall' between NATO and Russia; Russia thinks of Ukraine as a buffer zone between Russia and NATO. Putin wants NATO to reverse its invasions and turn the clock back to 1997. Putin says that NATO promised not to expand eastward but did so anyways. However, this may be a false claim since the instance was before the Soviet collapse in 1991. Moreover, the promise was made to then Soviet President Mikhail Gorbachev, when they discussed about NATO's expansion eastward but only in the context of East Germany(When Germnay was still seperated into East and West Germany).")
    st.markdown("What may be Putin/Russia's goal in this?")
    st.markdown("From the causes, in some aspects, we can see what they want: Take Ukraine back(They believe that Ukraine once belonged to the Russian Empire and they still do now; Russia does not accept that Ukraine is a soverign state). Another thing may be to weaken and stop Ukraine from joining NATO.")
    st.header("Affects on civilians and people")
    st.markdown('As we know, wars effec the world heavily, espcially if it is on this scale and is between 2 powerful countries. The economy and the amount of food becomes an issue for alot of civilians. Since Ukraine and Russia are big exports of wheat, barley, corn and cooking oil, to mainly African and Middle Eastern countries. Without these exports, food prices may skyrocket, or at least become higher. A lot of poor families may not be able to afford the food anymore and go hungry. This may also increase poverty rates in many countries since food prices are high, and some families may have spent all their money on food. Russia is also a big exporter of petroleum, and being hostile and different sides with Russia may mean losing a large part of their petroleum. Russia has already cut off petroleum supplies of 2 NATO countries Poland and Bulgaria along with Ukraine. As we may have noticed around the world, gas prices are going up since the supply is going down while the demand for natural gas is still very high. We can check specific changes from the image below that I have found on npr.org.')
    image_4 = Image.open('Screen Shot 2022-06-27 at 10.31.24 PM.png')
    st.image(image_4, caption = 'This image depicts specific changes that countries around the world are facing due to the Russo - Ukrainian war.')
    st.markdown("Also, 5.8 million people has fleed Ukraine due to the war in Ukraine. This is a huge increase in refugees. These people are living their homes and are now homeless. The good thing is that the UN is helping to take care of these refugees.")
    st.markdown("Moreoever, tension is also growing in the EU and UN when the countries are taking sides in this war. Also, Russia stocks are going down drastically since there was a ban on Russian stocks. This has severely affected the Russian economy and the civilians/Russians. The EU is also planning to put an oil embargo on Russia's oil. They also plan to ban or cut Russian energy imports, sanction Russian companies, etc.")
    st.markdown("In some ways, we can see that the world is not doing well due to the war and also COVID, but how are people's happiness effected by the war?")
    st.markdown("Today we are going to look at this World Happiness case study from the year 2005 - 2022 that analyzes the specific countrys' happiness based on various happiness factors. Now let's see how happiness is effected by the Russo - Ukrainian war or if there is a correlation between the two.")
###############3######################## Data Cleaaning#####################################
if selected == 'Data Cleaning':
    
    st.title('Data Cleaning')
    st.markdown('To start off, the most important thing to do is make sure that our data is fair and that it is a clear representation of what we are going to explore, which is the Russo - Ukrainian war. So for extra columns or rows that are unneeded, false, and unclear, it should either be changed or taken away from the data in order for us to analyze the data easier.')
    st.markdown('Below, first take a look at our datasets that we are going to, first, join together then clean and use. This dataset ranges from 2005 to 2022. With this amount of data, it would be easier for us to analyze how happy or unhappy either the Ukrainians or the Russians are and how it is effected and affects world events.')
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
    st.subheader('Importing the data')
    st.markdown("To analyze a piece of data we first need to read in the csv file containing all the data that we need. To do this, we can use this code: ")
    
    code_1 = '''happiness_2021 = pd.read_csv('world-happiness-report-2021.csv')
    happiness_2005 = pd.read_csv('world-happiness-report.csv')'''
    st.code(code_1, language='python')
    
    st.caption("The way this works is by giving the file path from your laptop to spyder(the software used to python programming) so that spyder can find and access the file. Currenlty I am only reading in the first 2 csvs that I will be using which is the happiness analysis dataset for 2021 and the happiness analysis dataset for 2005.")
    
    st.caption("I didn't read in the csv for 2022 since at the time when I have started this analysis, the data for 2022 isn't yet available.")
    
    
    st.subheader('Data Cleaning for 2 datasets')
    st.markdown("When we first read/see a dataset, we must carefully go through it and perceive issues or mistakes the dataset contains and try to fix them. In this dataset, I have noticed a number of issues that must be fixed in order for us to have a fair analysis of the data.")
    
    st.markdown("Some issues that we have encountered when looking at this dataset:")
    st.markdown("1. Some of the countries present in one dataset isn't in the other dataset")
    st.markdown("2. Some of the columns present in one dataset isn't in the other one ")
    st.markdown("3. Even if the columns are the same data the columns may be named differently")
    st.markdown("4. There may just be random mistakes such as empty columns for just some of the data.")
    st.caption(" - This is presented more extensively in the 2022 dataset.")
    st.markdown("5. There are extra columns that are unnecessary for our analysis.")
    
    st.markdown("First of all, for the problem of having countries that are present in one dataset and not the other, and then take the code out. We can do this by using this code:")
    code_2 = '''countries_dict = [country for country in happiness_2005
                    ["Country name"].unique() if country in happiness_2021["Country name"].values]
    happiness_2005 = happiness_2005.loc[happiness_2005["Country name"].isin(countries_dict)].reset_index(drop=True)'''
    st.code(code_2, language = 'python')
    st.caption("We can do this by creating a dictionary called countries_dict. Countries dict makes a list of countries in the 2005-2020 dataset that is also present in the 2021 dataset cause they are not the same (Some coutnries in the 2005-2020 datset are not in the 2021 dataset). So in order to properly analyze them, we are going to make the countries the same by finding out the countries that are present in both datasets and modify one dataset to fit the other datase's countries. Since the 2021 happiness dataset has less countries and that it is easier to take out then add, we will modify the 2005-2020 dataset to fit the 2021 dataset. The next line of code takes out the countries that we have just added into countries dict from the 2005-2020 dataset.")

    st.markdown("Furthermore, we are missing a key column that is of utmost importance when analysing the data especially analyzing through plots and graphs later on. It also clarifies the data for the viewer after we have merged all the columns from 2005-2022. This is the 'year' column.")
    st.code('''happiness_2021["year"] = 2021 ''')
    st.caption("This part is just the pyton code for adding a new column and giving it a value. We have all the value in this column of year for the 2021 dataset to be '2021' since we only gave it one input. If we want different inputs for each column, then we have to place a list here for each input of the column.")
    st.markdown("Next, we need to rename the columns so that the columns in the data for 2021 matches the columns for the data in the 2005-2020 dataset.")
    st.code('''happiness_2021.rename({"Ladder score":"Life Ladder",
                          "Healthy life expectancy":"Healthy life expectancy at birth",
                          "Logged GDP per capita":"Log GDP per capita"}, axis=1, inplace=True)''')
    st.markdown("After renaming the columns, we want to take out the ones that we don't want in this data analysis. But before we start dropping it out, we should make a list of the columns that we want by keeping only the ones that we do want.")
    st.code('''columns = list(happiness_2005.drop(["Positive affect", "Negative affect"], axis=1).columns) + ["Regional indicator"]''')
    st.caption("We did this by making a list of the names of the columns in the 2005-2020 dataset without the ones that we don't want and adding in the regional indicator column. This doesn't directly change the 2005 dataset since we didn't add inplace = True.")
    st.markdown("Then we want to combine the 2005 and 2021 dataset, but only combining the columns that we chose in the line previously(meaning we don't take the columns that is only present in 2021 and aren't in 2005. Also we are going to add the regional indicator column to the 2005 dataset. We do this since the 2005 one doesn't have it.)")
    st.code('''happiness = pd.concat([happiness_2005, happiness_2021[columns]])''')
    st.caption('We have merged the 2 datasets together(the 2005-2020 dataset and the 2021 dataset)using the concat function. For the 2021 dataset, we are merging only the columns that we have chosen in the previous list.')
    st.markdown("As we did more looked through the data even more, we realized there were various countries that were different. As we searched them up, we realized that they were the same country but under a different name. The country Swaziland has changed its name in 2008 to Eswatini. It wasn't recorded in the 2005-2020 dataset but the name change was recorded in the 2021 dataset. Thus, we need to change the names so that it is current.")
    st.code('''happiness_2021.replace({'Swaziland': 'Eswatini'},inplace =True)
    happiness.replace({'Swaziland': 'Eswatini'},inplace =True''')
    st.caption("In the first line of code, we replace Swaziland with Eswatini from the 2021 Happiness dataset, the inplace = True replaces it in the original dataset. Then we replace it from the big dataset which also replaces Swaziland in the 2005-2020 dataset.")
    st.markdown("Now we are going to make a list of the country names and regional indicator values for each of these countries. This is for later on when we merge the 2022 dataset since this one doesn't have the regional indicator column.")
    st.code('''regional_dict = {k:v for k,v in zip(happiness_2021["Country name"], happiness_2021["Regional indicator"])}''')
    st.caption("Here we are using dictionary comprehension, to make a list/dictionary that pulls the names and regional indicator of the countries in the 2021 dataset. ")
    st.markdown("However, we realized a problem: Congo does not have a regional indicator. Thus, we need to manually add a regional indicator for Congo.")
    st.code('''regional_dict.update({'Congo':'Sub-Saharan Africa'})''')
    st.dataframe(happiness.loc[happiness['Country name']== 'Congo'])
    st.caption("Now we are adding the regional indicator of Congo which is Sub - Suharan Africa.We are adding this into our dictionary that we have created in the previous cell. But remember we haven't made any changes to the actual table yet(above is only an example of what it would look like afterwards).")
    st.markdown("Then we want to apply the regional dict that we have created before to the 2005-2020 dataset and the 2021 dataset together collectively since the 2005-2020 dataset doesn't have one. It is important for us to have it since we will be needing it for later analyzing the data and also graphing the data.")
    st.code('''happiness["Regional indicator"] = happiness["Country name"].replace(regional_dict)''')
    st.caption("We have added a new column. And we are applying the regional indicator that we pulled out of 2021 and applying it to the 2005 and 2021 dataset to the happiness dataset.")
    st.markdown("Now it is finally time for us to drop the columns that we don't want out of the dataset. These are the columns postitive and negative affect which we don't need for our analysis.")
    st.code('''happiness.drop(["Positive affect","Negative affect"], axis = 1, inplace = True)''')
    st.caption("Before we had made a list with names of columns that we do want and a regional indicator, but haven't actually dropped the columns that we don't want from the dataset. Now we have actually dropped the columns that we don't want from the dataset.")
    st.subheader("New data")
    st.markdown("Just around March 2022, the ***World Happiness Report 2022*** has came out and in order for us to better evaluate the Ukrain,  Russia crisis and its affect on people of their country we should add it into our currently merged 2005-2021 dataset. ")
    st.markdown("To do this, we should first read in the data from our laptop.")
    st.code("happiness_2022 = pd.read_csv('DataScience/2022.csv')")
    st.caption("This is the code that uses pandas to read in csvs of the data that we want to use.")
    st.markdown("Then we realized a problem: In front of some column names, there are the text of 'Explained by:', we need to remove them in order for all the column names to be the same throughout all 3 datasets in order to make it possible for python to merge and later graph them properly. ")
    st.code("happiness_2022.columns = happiness_2022.columns.str.replace('Explained by: ', '')")
    st.caption("We will use the replace function to replace the 'Explained by' by a blank space that will get rid of the 'Explained by' in the 'Explained by' in the columns." )
    st.markdown("After this, we have to go through many of the processes that we went through before with the other 2 datasets. First of all, we are going to be making a dictionary of column names that we want to change in order for the column names to be the same with the happiness dataset(merged dataset).")
    st.code('''happiness_2022_replace = {'Country': 'Country name','Happiness score':'Life Ladder',
                            'GDP per capita': 'Log GDP per capita',
                             'Healthy life expectancy':'Healthy life expectancy at birth'}''')
    st.caption("This is the code that we have used to create a dicitonary/list of the original column names and the ones that we want to replace it with . REMEMBER: We haven't replaced anything or dropped anything at this point yet, this is just MAKING A LIST. You can see this either my viewing the entire line of code, or the fact that there isn't an 'Inplace = True'. You add Inplace = true when you want to make permanent changes to the dataset. ")
    st.markdown("Now we are going to add a column called 'year' to the Happiness 2022 dataset. The value for each row of the 'year' column is always 2022. THis will be useful for various reasons later on in the data analysis and will clarify things extensively especially after we merge all the 3 datasets together, with the years spanning from 2005-2022.")
    st.code('''happiness_2022['year'] = 2022''')
    st.caption('This is the code that we use to add columns to a dataset and after the equals sign we add a list of the values that we want to input into each row of this column. Since we want all the inputs for all the countries in the dataset to be 2022, we will only input 2022.')
    st.markdown("But we have encountered another issue through scrolling through the dataset(we often find alot of errors and problems with the dataset when we are scrolling and looking throught it). Some of the counteries randomly has an asterisk in front of it and now python doesn't recognize the countries anymore which is a an issue. We can use the code below to remove the asterisk.")
    st.code('''happiness_2022['Country'] = happiness_2022['Country'].str.replace('*', '', regex = True)''')
    st.caption("We are using the 'replace' function again which will replace something with something else. We are replacing the asterisk with a space that will take out the asterisk. The inplace = True is there as always when we want to make changes to something. It actually makes changes to the data itself.")
    st.markdown("Now we are actually going to be dropping the columns from the World Happiness dataset by using the dictionary that we have created before.")
    st.code('''happiness_2022.rename(happiness_2022_replace, axis = 1, inplace = True)''')
    st.caption("We are now using the renaming function along with the the dicitonary  that we have created earlier. The axis = 1 is just there to remind the code that we are editing the columns not the rows. The Inlace = True, as always, is there to tell python that we want to make permanent changes to the dataset.")
    st.markdown("But we are still not ready for merging the datasets since minor errors and problem are still present in the dataset that may be a mistake but we have to fix them in order for everything to run and work properly.")
    st.markdown("I found that there is a great issue in the statistics of the World Happiness Data 2022, which is the way that the numbers are written. Normally, decimals are written with a '.', but here however, they write it with ','. This makes python unable to comprehend this as a decimal/float but as a string. In order for us to calculate we need to change it into a float with a decimal point and not commas.")
    st.code('''happiness_2022.replace({',': '.'}, inplace = True, regex =  True)''')
    st.caption("We are again using the replace function that replaces all the commas in the World Happiness 2022 Dataset to periods.")
    st.markdown("Next, we need to change the names of countries that are different in the World Happiness 2022 dataset so that they match the ones in the other 2 merged dataset.")
    st.code('''happiness_2022.replace({'Czechia':'Czech Republic','Eswatini. Kingdom of':'Eswatini'}, inplace = True)''')
    st.caption("We are direclty replacing names of columns using the replace function with inplace = True with makes a direct and permanent change to the original dataset.")
    st.markdown("However, even though we have changed the comma to a decimal point, python cannot automatically comprehend that it is now a decimal/float and not a stirng. What we need to do to make python understand that it is now a decimal is by using the code below.")
    st.code('''happiness_2022[[col for col in happiness_2022.columns if col != 'Country name']]= happiness_2022.drop('Country name', axis 1).astype(float)''')
    st.caption("The code above means for every column in the World Happiness 2022 Data that is not the column 'Country name' will be equal to: to a float. To do this we will be dropping the 'Country name' column since it is made up letters/string and cannot be converted to a float. Then using the astype functon to convert it into a float. The astype converts the remaining numbers into a float which tells python that these are decimals.  ")
    st.markdown("Another issue we saw when scrolling through the dataset was that the last row of the dataset was corrupted and empty. Since we don't be needing it anymore, we should drop this row.")
    st.code('''happiness_2022.drop(index = [146], inplace = True, axis = 0)''')
    st.caption("This is the code that we used to drop the row with the index number 146 since there is nothing in it. We are using inplace = True as to make permanent changes to the entire data of the Happiness 2022. The axis = 0 lets python know that we are editing the rows and not the columns. ")
    st.markdown("Now, we have finally started coming towards the step to preparing to merge the 3 datasets. We are going to find out the columns from the 2022 dataset that is also present in the 2021 dataset so that we can merge successfully.")
    st.code('''happiness_2022 = happiness_2022[[col for col in happiness_2022.columns if col in happiness.columns] ]''')
    st.caption("This is the code that we used to find the same columns. This works by making a list out of every column of Happiness 2022 that is also in the Happiness 2021 dataset.")
    st.markdown("Now it is time for the actualy merging of the happiness dataset(Happiness 2005-2020 and the 2021 Happiness Dataset).")
    st.code('''happiness = pd.concat([happiness,happiness_2022])''')
    st.caption("pd.concat here is used to merge the 2 datasets that we have chosen together.")
    st.markdown("")
    st.code('''happiness = pd.concat([happiness,happiness_2022])''')
    st.caption("We have merged the 2 datasets together.")
    st.markdown("Right now we will be needing to apply the regional indicator to the merged happiness dataset. We are doing this because we noticed that the World Happiness 2022 dataset does not have a regional indicator.")
    st.code('''happiness["Regional indicator"] = happiness["Country name"].replace(regional_dict)''')
    st.caption("In this line of code, we are taking the column of regional indcator in happiness and replacing the regional indicator using the country name(we created a regional dict that has the country name and the regional indicator. We can replace the new regional indicator by merging through the country names).")
    st.markdown("We will be converting all the years(numbers) into integers because currently much numbers are displayed, for example, as 2022.0. This is not as easy to read for the viewers. So, converting it into an integer makes it easier to read.")
    st.code('''happiness['year'] = happiness['year'].astype(int)''')
    st.caption("This is the code that takes the year column of happiness(the merged one) and converts the inputs in the year column into integers/ints.")
    st.markdown("We are going to sort the year and country names. First viewing the year and all the countries in that year(by alphabetical order) and then going to the next year. this is necessary for using the animation frames in the visual representation/plotly part of the data analysis.")
    st.code('''happiness = happiness.sort_values(['year','Country name']).reset_index(drop = True)''')
    st.caption("This is the code that sorts the values by alphabetical order,first the year, and then the countries. Then we are going to reset the index because after merging and cleaning the dataset, the rows have moved from their original places which makes the index number mixed up. We need to reset the index numbers so that they match the current order.")
    st.markdown("Now we have a good and cleaned dataset that is fair and we can begin our analysis of the data through visualizations and real world connections.")
######################################################Plots and Graphs for the General World########################################################
if selected == 'Plots and Graphs for the General World':
    st.title('Plots and Graphs for the General World')
   
    st.markdown('Now that we understand how our current dataset came to be what it is. We still may not have a complete idea on the data. The best way of understanding a data may be visual representations. Below are some visual representations of the happiness data with all the countries in it so you can play around and get familiar with the data before moving on.')
    st.markdown("Here is a pie chart. A pie chart shows a part-to-whole relationship in a data. In this pie chart, you can pick any happiness factor for a region and compare the percentages between regions. The pie chart will add the statistics of each region and compare this region's statistics to the statistics of all the regions. This works by python adding in all the values of a column with the same regional indicator and making a pie chart out of it.")
    generosity_pie = happiness.copy()
    generosity_pie['Generosity']= generosity_pie['Generosity']+1
    pie_chart_select = st.selectbox('Choose a happiness factor',  ['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption'])
    fig_pie = px.pie(generosity_pie, 'Regional indicator', pie_chart_select, height = 600, width = 1000, title = 'Happiness Scatter Plot for Countries Around the World')
    st.plotly_chart(fig_pie)
    
    if pie_chart_select == 'Life Ladder':
        st.caption('When we have chosen the happiness factor of Life ladder, which is a general representation of happiness, we can see that Western Europe has the highest life ladder due to a percentage of 17.9%. It is closely followed by Sub-Saharan Africa(16.7%), then by Latin America and Carribean(15.9%), etc, with South Asia having the lowest in Life Ladder(General happiness indicator). ')
    
    if pie_chart_select == 'Log GDP per capita':
        st.caption("When we have chosen the happiness factors of Log GDP per capita which is similar to an approximation of GDP growth that is valid for small growths. We can see that West Africa is the highest in Log GDP per capita. The reason to this may be because of Africa's recent year's growth in sales of commodities and goods which leads them to a high log GDP per capita. Western Europe also has a fairly high overall log GDP per capita because of its inclusion of 'agriculture and manufacturing, plus high-tech and service industries', according to Geography")
   
    #######################################Scatter Plot#########################################
    st.markdown("Here is a scatter plot where you can view points in each year of time of each country through analysing their happiness factor. Play around and see if you can find and learn something new.")
    x_axis_scatter = st.selectbox('Choose a x axis happiness factor for this scatter plot',  ['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption'])
    y_axis_scatter = st.selectbox('Choose a y axis happiness factor for this scatter plot',  ['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption'])
    gdp_plot = px.scatter(happiness, x= x_axis_scatter, y= y_axis_scatter, color = 'Regional indicator',  hover_name = 'Country name', height = 600, width = 1000, title = 'Happiness Scatter Plot for Countries Around the World'
              )
    st.plotly_chart(gdp_plot)

    st.markdown("below is a 3D scatter plot that is interesting to see since we are comparing 3 happiness factors to each other. Play around and check what you can see.")
    
    col5,col6,col7=st.columns(3)
    world_scatter_3d_x = col5.selectbox("Select a **X VALUE** happiness factor for this 3D scatter plot",['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption'])
    world_scatter_3d_y = col6.selectbox("Select a **Y VALUE** happiness factor for this 3D scatter plot",['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption'])
    world_scatter_3d_z = col7.selectbox("Select a **Z VALUE** happiness factor for this 3D scatter plot",['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption'])
    fig_3d_scatter_world = px.scatter_3d(happiness, x=world_scatter_3d_x, y=world_scatter_3d_y, z=world_scatter_3d_z,color='Regional indicator', height = 800, width = 1000,title = '3D Plot for General World Analysis')
    st.plotly_chart(fig_3d_scatter_world)
    
    st.markdown("Below we have a box plot where you can see for each factor which year has the highest or lowest of each happiness factor as compared to other countries. You can view the median, min, and max. You can check with the dataframe on the introduction page to tell which country it corresponds with.")
    
    box_world = st.selectbox('Choose a happiness factor for the box plot',['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption'])
    st.plotly_chart(px.box(happiness, 'Regional indicator', box_world, hover_name = 'Country name', color = 'Regional indicator', color_discrete_sequence = px.colors.qualitative.Light24, width = 950, height = 500,animation_frame = 'year', title = 'Box Plot for General World Analysis'))
    st.markdown("Now, let's look at a chloropleth map that analyzes countries based on their happiness factors but as compared to all the other countries in the world. If you hover on the country with your cursor, you can see which country it is. And scrolling the bar below can change the year.")
#################choloropleath - world##############################
    world_chloro = st.selectbox('Select a happiness factor from the following list for the chloropleth map',  ['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption'])
    fig2 = px.choropleth(happiness,locations = "Country name",
                         locationmode = "country names",color = world_chloro,
                         animation_frame = "year",
                       height = 600, width = 1000)
    #fig.update_geos(fitbounds="locations", visible=False)
    #fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig2)
    
####################################Plots and Graphs for Ukraine and Russia#########################################################
if selected == 'Data Analysis':
    st.title('Data Analysis')
    
    st.markdown("Now let's officially look at the analysis of Ukraine and Russia: How the Russo - Ukrainian war may have impacted the people's happiness.")
    st.markdown("To start off, let's first look at a 3D scatter plot. A 3D scatter plot, when used here, displays the relationship between 3 variables measuring the happiness of Ukraine and Russia. A 3D scatter plot is just interesting since you can see the relationship between 3 factors of happiness and freely give your own explanation here.")
    col8,col9,col10=st.columns(3)
    world_scatter_3d_x = col8.selectbox("Select a **X VALUE** happiness factor for this 3D scatter plot",['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption'])
    world_scatter_3d_y = col9.selectbox("Select a **Y VALUE** happiness factor for this 3D scatter plot",['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption'])
    world_scatter_3d_z = col10.selectbox("Select a **Z VALUE** happiness factor for this 3D scatter plot",['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption'])
    fig_3d_scatter_world = px.scatter_3d(happiness.loc[happiness['Country name'].isin(["Russia","Ukraine"])], x=world_scatter_3d_x, y=world_scatter_3d_y, z=world_scatter_3d_z,color='Country name', height = 600, width = 800, animation_frame = 'year')
    st.plotly_chart(fig_3d_scatter_world)
    st.caption("**Please check below for the analysis of this 3D scatter plot of Russia and Ukraine.**")

    st.markdown("After you have looked through and tested quite a few of these, you may notice that there is something that we can note in common. That is, no matter what x,y,z value we click, we can see that Ukraine and Russia's dot are very far apart. Noting this, we can see how these two countries are ver different. Scrolling through the years, we can notice many patterns:")
    st.markdown("1. When any of the values are equal to Life ladder, we can see that Ukraine has a higher Life ladder value as compared to the happiness value of Russia up till 2009. Then, Russia in 2010, surpasses them. Since 2014, Ukraine's life ladder has been very low. We can interpret this to be because of the **Annexation of Crimea**. We can see that Russia seems to have a very high Life ladder for the year 2014 since they successfully took over Crimea. It is slowly rising througout the years after the annexation of Crimean. Then in 2022, there is also the Russo - Ukrainian warfare 'which made the Ukrainians unhappy. ' ")
    st.markdown("2. However, here, in this criteria of study, Russia seems to have a higher Log GDP per capita. This may be because Russia is an overall, wealthier country as compared to Ukriane. Also，Russia in some ways are full of natural resources on its vast pieces of land. Russia and Ukraine's dot on the 3D Scatter Plot are very far apart. They often are at complete opposite ends of each other.  ")
    st.markdown("3. When we look at Social Support it is not very much always the same country that ranks higher. Before 2007, Ukraine has higher social support than RUssia, but in 2007, we can see that Ukraine now has a much lower social support as compared to Russia. This may be because in 2007, there was a political crisis in Ukraine between 2 big ideologies at the time: Pro-Western or Pro-Russian. This may be the reason that Ukrainians may feel that during this year, they have a lower social support. In 2013, everything started going back and Ukraine now has more social support as compared to Russia. But in 2014, Ukraine started to not have as much social support as Russia. This may be the effect of the annexation of Crimea and things that followed after like COVID and the Russo-Ukrainian war. However, the good news is that we can still see the Russia and Ukraine growing in their social support. ")
    st.markdown("4. For the healthy life expectancy, we can see that before 2022, Ukraine has always been ahead of Russia and both countries were steadily growing in their healthy life expectancy. However, in 2022, there is a huge drop in the healthy life expectancy of both countries, especially Ukraine. Once surpassing Russia for years in this area, now fell so much that it is behind Russia. From this we can see how the war has influenced new born babies and children in both countries.")
    st.markdown("5. In the freedom to make life choices critera, Russia seems to have a higher freedom to make life choices. Since freedom of media and sexual diversity has always been an highly debated and issue in Ukraine, thus there isn't much freedom of choice in Ukraine. However, the good thing that we can notice is that it is always growing.")
    st.markdown("6. Russia also seems to have more generosity since as we have just said that Ukraine is having issues with sexual diversity and freedom of media, this may be why they don't have a generosity level of as high as Russia. However, it is growing just like the world is everchanging, and evolving in order to create a better place with more generosity and allowance for all people.")
    st.markdown("6. Before 2013, Ukraine seems to have a higher level of corruption. However, after 2013, Russia seems to be more corrupt. Even now, according to the Transparency International's 2021 Corruption Perceptions Index, Russia seems to be the most corrupt in the country in the world right now, and Ukraine at 2nd. The sad thing is that the numbers don't seem to be decreasing on the perceptions of corruption.")

        

    box_world = st.selectbox('Choose a happiness factor for the box plot',['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption'])

    st.plotly_chart(px.box(happiness.loc[happiness['Country name'].isin(["Russia","Ukraine"])], 'Country name', box_world, hover_name = 'Country name', color = 'Country name', color_discrete_sequence = px.colors.qualitative.Light24, width = 950, height = 500))
######################## Closest country prediction graph###################################
    st.markdown("In this closest line prediciton, you can freely explore which countries are closest to another country depending on the happiness factors. You can observe how they compare throughout the years. Before playing with it freely, please remember to first try out Ukraine and Russia.")
    Country = st.text_input('Choose a country', 'Ukraine')
    k =int(st.text_input('Enter the number of neighbors closest to this country',5))
    happiness_factor = st.selectbox('Select a happiness factor from the following list',  ['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption'])
    country_line_fig =  country_line(Country, k, happiness_factor)
    st.plotly_chart(country_line_fig)
    if Country == 'Ukraine':
        st.caption("We can see with Ukraine, it is closest to countries that are in Eastern Europe, parts of Africa, and the Americas. This may be because Ukraine has been heavily influenced by countries that are part of the closest neighbors to Ukraine, in the past. Thus, we can see that culture is actually connected with happiness in some way. We can see from the line chart that Ukraine and its closest neighbor's healthy life expectancy at birth, Log GDP per capita, freedom to make life choices, and percpetions of corruption had all gone down drastically, towards 2020 or after. But generosity with Ukraine and all its closest neighbors seems to go up also in recent years. Life ladder and the other factors vary due to different circumstances.")
    if Country == 'Russia':
        st.caption("We can see that the countries closest to Russia were once with Russia in the Soviet Union. These countries, share with Russia an extensive amount of similarities in history. This shows how culture and history kind of influes how happy a country is. Russia and its neighboring countries in the sense of happiness have various happiness factors that have experienced a great drop in 2022: Log GDP per capita, healthy life expectancy at birth, freedom to make life choices, and perceptions of corruption. The rest except life ladder had all gone up. Life ladder really varies depending on events in the country and how people see things.")
    st.markdown("When you type any country in, please remember to capitalize it.")
    
    x_axis_map_ru = st.selectbox('Choose a happiness factor below', ['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption'])
    fig3 = px.choropleth(happiness.loc[happiness['Country name'].isin(["Russia","Ukraine"])],locations = "Country name",locationmode = "country names",color = x_axis_map_ru, animation_frame = "year")
    st.plotly_chart(fig3)
    if x_axis_map_ru == 'Life ladder':################it doens't work for life ladder
        st.caption('Before 2009, every year, Ukraine and Russia would exchange who was happier. But after that, Russia seemed to be happier and Ukraine to be much less happier. This may relate to the many problems that Ukraine has with both Russia and without: Gender diveristy, problems with Russia like annexation of Crimea etc. However, Russia seems to be very happy and the people seems to be very happy with its government leader: Putin. Thus, it is understandable in some way, why the statistsics are what they are.')
    elif x_axis_map_ru == 'Log GDP per capita':
        st.caption("Since Russia is a overall wealtheir and more economically developed country as compared to Ukraine, it is understandable that Russia, despite having large population, has a higher Log GDP per capita throughout the years. This may also be because Russia is bigger and has more natural resources. This can be seen with the fact that Russia accounts for 36% of the world's natural gas exports. Back to the Russo-Ukrainian war, without Russia's natural gases and oils, it is going to be a tough time for countries and civilians around the world.") 
    elif x_axis_map_ru == 'Social support':
        st.caption("Russia overall has a higher social support as compared to Ukraine, throughout the years. Which is still understandable, as considering that Russia is a wealthier and more developed country.")
    elif x_axis_map_ru == 'Healthy life expectancy at birth':
        st.caption("We can see that although Ukraine has a low birth rate(9.2 births per 1000), Russia has a even loweer one. However, in 2022, as the Russo-Ukrainian war is happening, we can see that Russia is having a higher birth rate. This may be because of the dangerous and hazardous environemnt in alot of parts in Ukraine. Many people lost their homes, bombs were dropped, people lost their lives, hospitals.. Well, it was harder to get health care overall.")
    elif x_axis_map_ru == 'Freedom to make life choices':
        st.caption("In the previous years, Russia tends to have a much higher freedom to make life choices as compared to Ukraine. Ukraine didn't have such a high fredom to make life choices due to many reasons that we have mentioned multiple times before. However, in 2021-2022, it decreased drastically. I believe that this is the work of COVID and the Russo-Ukrainian war. The public may finally be aware of what kind of person Putin is and what he wants and the little amount of freedom he gives.")
    elif x_axis_map_ru == 'Generosity':
        st.caption("Over the years, Ukraine seems to be more generous. Although there may not be a clear reason why Ukrainians seem to be more generous than Russians, we can say that the culture and all that may have influenced it.")
        range_color = [-0.5, 0.25]
    elif x_axis_map_ru == 'Perceptions of corruption':
        st.caption("We can see that Russia's perceptuion of corruption hasn't been very stable and nor has Ukraine's been very stable. This may be because of political etc events that have happened and caused this. Especially in 2014, when the annexation of crimea happened, we could notice that Russian beleive there were more corruption than Ukrainians beleived there were ecorruption.")
    else: 
        st.caption('Please select a happiness factor to analyze and view')
    
   
    st.markdown("Now let's look at a scatter plot for Ukraine and Russia that we can view from many aspects of a happiness factor in order to analyze it.")
    col11,col12 = st.columns([4,5])
    x_ru_scatter_plot = col11.selectbox('Choose a **X VALUE** for this Ukraine Russia scatter plot',['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption'])
    y_ru_scatter_plot = col11.selectbox('Choose a **Y VALUE** for this Ukraine Russia scatter plot',['Life Ladder', 'Log GDP per capita', 'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption'])
    
    if x_ru_scatter_plot == 'Healthy life expectancy at birth':
        x_range = [0,80]
    elif x_ru_scatter_plot == 'Life Ladder':
        x_range = [0,10]
    elif x_ru_scatter_plot == 'Social support':
        x_range = [0,1]
    elif x_ru_scatter_plot == 'Generosity':
        x_range = [-0.5,1]
    elif x_ru_scatter_plot == 'Log GDP per capita':
        x_range = [6,12]
    elif x_ru_scatter_plot == 'Perceptions of corruption':
        x_range = [0,1]
    elif x_ru_scatter_plot == 'Freedom to make life choices':
        x_range = [0,1]
    else:
        x_range = None

    if y_ru_scatter_plot == 'Healthy life expectancy at birth':
        y_range = [0,80]
    elif y_ru_scatter_plot == 'Life Ladder':
        y_range = [0,10]
    elif y_ru_scatter_plot == 'Social support':
        y_range = [0,1]
    elif y_ru_scatter_plot == 'Generosity':
        ange = [-0.5,1]
    elif y_ru_scatter_plot == 'Log GDP per capita':
        y_range = [6,12]
    elif y_ru_scatter_plot == 'Perceptions of corruption':
        y_range = [0,1]
    elif y_ru_scatter_plot == 'Freedom to make life choices':
        ange = [0,1]
    else:
        y_range = None
        
    col12.plotly_chart(px.scatter(happiness.loc[happiness['Country name'].isin(["Russia","Ukraine"])], x= x_ru_scatter_plot, y=  y_ru_scatter_plot, animation_frame="year" ,category_orders = {'year':np.arange(2005, 2022)},color="Country name", hover_name="Country name", size = 'year', range_x = x_range, range_y = y_range, size_max=12, width = 600, height = 500,title = 'Scatter Plot for Ukraine and Russia'))
    

#################################################################Conclusion#########################################################################
if selected == 'Conclusion':
    st.title('Conclusion')    
    st.markdown("Now that you have reached the end of this, have you formed your own opinion on whether the Russo- Ukrainian war has something to do with the happiness of Russia and Ukraine?")
