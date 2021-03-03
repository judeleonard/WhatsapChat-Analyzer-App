# -*- coding: utf-8 -*-
"""
This is a file to run analysis and create functions for visualization 


"""

import pandas as pd

import emoji
import collections as c
from collections import Counter
import streamlit as st

import plotly.express as px
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings('ignore')

from wordcloud import WordCloud, STOPWORDS

st.set_option('deprecation.showPyplotGlobalUse', False)




def authors_name(df):
    """
    This returns the name of individuals in chats

    Parameters
    ----------
    data : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """

    authors = df.Author.unique().tolist()
    return [name for name in authors if name != None]




def extract_emojis(s):
    """
    This function is used to calculate emojis in text and return in a list
    
    """
    
    return [c for c in s if c in emoji.UNICODE_EMOJI]




def stats(df):
    """
    This fucntion takes input as data and return total messages, links, media and emojis used in chat
   
    """
    
    total_messages = df.shape[0]
    media_messages = df[df['Message'] == '<Media omitted>'].shape[0]
    emojis = sum(df['emoji'].str.len())
    letter_count = sum(df['Message'].apply(lambda s : len(s)))
    word_count = sum(df['Message'].apply(lambda s : len(s.split(' '))))
    
    return "Total Messages: {} \n Total Media: {} \n Total Emojis: {} \n Letter Count: {} \n Word Count:{}".format(total_messages, media_messages, emojis, letter_count, word_count)



def popular_emoji(df):
    """
    This function returns the list of emojis with respect to their frequencies
    
    """
    total_emojis_list = list([a for b in df.emoji for a in b])
    emoji_dict = dict(Counter(total_emojis_list))
    emoji_list = sorted(emoji_dict.items(), key=lambda x: x[1], reverse=True)
    return emoji_list



def visualize_emoji(df):
    """
  This functions generates the pie chat plots for popular emojis  

    """

    emoji_df = pd.DataFrame(popular_emoji(df), columns=['emoji', 'count'])
    fig = px.pie(emoji_df, values='count', names='emoji')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig



def word_cloud(df):
    """
    Function to generate sentiment analysis with wordcloud
    
    """
    df = df[df['Message'] != '<Media omitted>']
    df = df[df['Message'] != 'This message was deleted']
    words = ' '.join(df['Message'])
    processed_words = ' '.join([word for word in words.split() if 'http' not in word and not word.startswith('@') and word !='RT'])
    # handling punctuations
    wordcloud = WordCloud(stopwords=STOPWORDS, background_color='black', height=643, width=800).generate(processed_words)
    
    fig = plt.figure()
    ax = fig.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    return fig
    


def active_date(df):
    """
    This function is used to generate a horizontal bar graph between date and 
    number of messages dataframe.

    Parameters
    ----------
    data : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    fig, ax = plt.subplots()
    ax = df['Date'].value_counts().head(10).plot.barh()
    ax.set_title('Top 10 active date')
    ax.set_xlabel('Number of messages')
    ax.set_ylabel('Date')
    plt.tight_layout()
    return fig
   
    


def active_time(df):
    """
    This function is used to generate a horizontal barplot between dates and number of messages in dataframe.

    Parameters
    ----------
    data : dataframe
        A function to create a horizontal bar plot

    Returns
    -------
    None.

    """
    fig, ax = plt.subplots()
    ax = df['Time'].value_counts().head(10).plot.barh()
    ax.set_title('Top 10 active Time')
    ax.set_xlabel('Number of messages')
    ax.set_ylabel('Time')
    plt.tight_layout()
    return fig
   


def day_wise_count(df):
    """ 
    Parameters
    ----------
    data : Dataframe
         This function generates a line polar plot of day count.

    Returns
    -------
    None.

    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_df = pd.DataFrame(df["Message"])
    day_df['day_of_date'] = df['Date'].dt.weekday
    day_df['day_of_date'] = day_df["day_of_date"].apply(lambda d: days[d])
    day_df["messagecount"] = 1
    
    day = day_df.groupby("day_of_date").sum()
    day.reset_index(inplace=True)
    
    fig = px.line_polar(day, r='messagecount', theta='day_of_date', line_close=True)
    fig.update_traces(fill='toself')
    fig.update_layout(
    polar=dict(
        radialaxis=dict(
         visible=True,
        )),
        showlegend=True
        )
    return fig



def num_messages(df):
    """

    Parameters
    ----------
    data : Dataframe
        This function generates the line plot of number of messages on monthly basis.

    Returns
    -------
    None.

    """
    df.loc[:, 'MessageCount'] = 1
    date_df = df.groupby("Date").sum()
    date_df.reset_index(inplace=True)
    fig = px.line(date_df, x="Date", y="MessageCount")
    fig.update_xaxes(nticks=20)
    
    return fig



def chatter(df):
    """
    

    Parameters
    ----------
    data : Dataframe
        This function generates bar plot of top 10 memebers invovled in a chat corresponding to the number of messages. 

    Returns
    -------
    None.

    """
    auth = df.groupby('Author').sum()
    auth.reset_index(inplace=True)
    fig = px.bar(auth, y='Author', x= 'MessageCount',color='Author', orientation='h',
                 color_discrete_sequence=['red','green','blue','goldenrod','magenta'],title='Number of messages relative to Author'
                 )
    return fig