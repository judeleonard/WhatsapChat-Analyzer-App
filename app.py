import streamlit as st
import pandas as pd
from modules import funct as fx

import plotly.express as px
import matplotlib.pyplot as plt

import re
import csv
from PIL import Image

st.set_option('deprecation.showPyplotGlobalUse', False)  # disable deprecation warnings from matplotlib

##--------------------------- Creating basic streamlit features-----------------------------------------------------#

img = Image.open('images(1).jpeg')
st.title('Whatsapp Group Chat Analysis')
st.image(img)
st.markdown('This Web App Runs Analysis on Exported Whatsapp Chat to Understand Texting Patterns of Users. Tap on the arrow icon by the upper left for more options')
st.set_option('deprecation.showfileUploaderEncoding', False) # disable warnings trying to convert file from byte to stringIo


st.sidebar.title('Explore Your Chat: :heart_eyes:')
st.sidebar.markdown('This App Analyzes Individuals or Whatsapp Group Chats :grinning:')

st.sidebar.markdown('[![Jude Leonard](https://img.shields.io/badge/Author-@Judeleonard-gray.svg?colorA=gray&colorB=dodgerblue&logo=github)](https://www.twitter.com/JudeLeonard13/)')

st.sidebar.markdown('### Follow the steps to export your whatsapp chat file.### :point_down:')
st.sidebar.text('1) Open Individual or group chat.')
st.sidebar.text('2) Tap options -> More -> Export Chat.')
st.sidebar.text('3) Choose export without media.')
st.sidebar.text('4) Ensure the group member names are saved before exporting.')
st.sidebar.text('5) Thats it!You good to go.')
st.sidebar.subheader('**FAQs**')
st.sidebar.markdown('*** Does this violate Privacy,what happens to my data?*** :confused:')
st.sidebar.markdown('Your uploaded data is not saved anywhere on this site or to any 3rd party, and can only be accessed by the uploader.')

#===================== Create widget drop down menu for date format==================================#
st.sidebar.markdown('**Upload Your Whatsapp Chat text file:** :file_folder:')
date_format = st.sidebar.selectbox('Please select the date format of your file before uploading your .txt file:',
                         ('mm/dd/yyyy', 'mm/dd/yy',
                           'dd/mm/yyyy', 'dd/mm/yy',
                            'yyyy/mm/dd', 'yy/mm/dd'))



#================== Extract data from text file using Regex and data cleaning=========================================

def getDataPoint(line):
    """
      function to extract date, time, author and message from line.

    Parameters
    ----------
    line : TYPE
        DESCRIPTION.

    Returns : date, time, author,message
    -------

    """
    splitLine = line.split(' - ')

    dateTime = splitLine[0]

    if ',' not in dateTime:
        dateTime = dateTime.replace(' ', ', ', 1)

    date, time = dateTime.split(', ')

    message = ' '.join(splitLine[1:])

    splitMessage = message.split(': ')
    author = splitMessage[0]
    message = ' '.join(splitMessage[1:])
   
    return date, time, author, message



def main():

    uploaded_file = st.file_uploader("", type=["txt"])
    
    
    global df
    if uploaded_file is not None:
         x = uploaded_file.read().decode("utf-8")
         content = x.splitlines()

         chat = [line.strip() for line in content]    # remove trailing white spaces from line
         clean_chat = [line for line in chat if not "joined using this" in line]  # remove join message warnings
         clean_chat1 = [line for line in clean_chat if not "created group" in line]  # remove message warnings about who created the group
         clean_chat2 = [line for line in clean_chat1 if not "changed this group" in line] # remove message warnings about who changed the group's icon
         clean_chat3 = [line for line in clean_chat2 if not "changed the subject" in line] # remove message warnings about who chnaged the subject
         clean_chat4 = [line for line in clean_chat3 if not "added" in line]     # remove messsge warnings about who added who
         clean_chat5 = [line for line in clean_chat4 if not "removed" in line]    # remove message warnings about who removed who
         clean_chat6 = [line for line in clean_chat5 if not "left" in line]        # remove message warnings about who left the group
         clean_chat_final = [line for line in clean_chat6 if len(line) > 1]
        
         data = []
         messageBuffer = []
         date, time, author = None, None, None
         
         
         for line in clean_chat_final:
              if re.findall("\A\d+[/]", line):         
                 if len(messageBuffer) > 0:    
                     data.append([date, time, author, ' '.join(messageBuffer)])
                 messageBuffer.clear()  # clear mesage data so it can be used for the next message
                 date, time, author, message = getDataPoint(line)
                 messageBuffer.append(message)        
              else:
                 messageBuffer.append(line)
         
         
         
         df = pd.DataFrame(data, columns=['Date', 'Time', 'Author', 'Message'])
         df = df.drop([0,1], axis = 0).reset_index(drop=True)  # to delete rows that contain messages about end to end enrcypted and who created group.
         df["Date"] = pd.to_datetime(df["Date"])
         df['Letter_Count'] = df['Message'].apply(lambda s : len(s))
         df['Word_Count'] = df['Message'].apply(lambda s : len(s.split(' ')))
         df['emoji'] = df["Message"].apply(fx.extract_emojis)



    

    try:
         
       if df.empty:
          st.error("Please upload a WhatsApp chat file!")
        
       if st.sidebar.checkbox("Show raw data", False):
          st.write(df)





        #=============================================================    
        # Names of members that participated in a chat
    
       st.sidebar.markdown("## To Analyze select :sunglasses:")
       names = fx.authors_name(df)
       names.append('All')
       member = st.sidebar.selectbox("Member Name", names, key='1')
             
       if not st.sidebar.checkbox("Hide", True):
        
             if member == "All":
                 st.markdown("## Analyze {} Members Together:".format(member))
                 st.markdown(fx.stats(df), unsafe_allow_html=True)
                 
                 
                 
                 st.markdown('**Word Cloud:**')
                 st.text("This will show the most used word in chat, the larger the wordsize the more often it is used.")
                 st.pyplot(fx.word_cloud(df))
        

                 st.write('**Number of messages as times move on**') 
                 st.plotly_chart(fx.num_messages(df))
        

                 st.write('**Day wise distribution of messsages for {}:**'.format(member))
                 st.plotly_chart(fx.day_wise_count(df))
                
                
                 st.write('** Most active date:**')
                 st.pyplot(fx.active_date(df))

                 
                 st.write("** Top 10 frequently used emojis:** :blush:")
                 emoji = fx.popular_emoji(df)
                 for e in emoji[:10]:
                     st.markdown('**{}** : {}'.format(e[0], e[1]))
                 
                    
                 st.write('** Visualize emoji distribution in pie chart:**')
                 st.text('Hover on Chart to see more details')
                 st.plotly_chart(fx.visualize_emoji(df), use_container_width=True)

                         
                 st.write('**Most active time for Chat:**')
                 st.pyplot(fx.active_time(df))
                 

                 st.write('**Chatter: Most active person in the group**')
                 auth = df.groupby('Author').sum()
                 auth.reset_index(inplace=True)
                 fig = px.bar(auth, y='Author', x= 'MessageCount',color='Author', orientation='h',
                              color_discrete_sequence=['red','green','blue','goldenrod','magenta'],title='Number of messages relative to Author'
                              )
                 st.plotly_chart(fig)


             else:
                 member_data = df[df['Author'] == member]
                 st.markdown("## Analyse {} chat:".format(member))
                 st.markdown(fx.stats(member_data), unsafe_allow_html=False)


                 st.write("** Top 10 popular emojis used by {}:**".format(member))
                 emoji = fx.popular_emoji(member_data)
                 for e in emoji[:10]:
                     st.markdown('**{}** : {}'.format(e[0], e[1]))


                 st.write('** Visualize emoji distribution in pie chart for {}:**'.format(member))
                 st.plotly_chart(fx.visualize_emoji(member_data))


                 st.markdown('**WordCloud:**')
                 st.text(" This will show most used words by {}.".format(member))
                 st.pyplot(fx.word_cloud(member_data))


                 st.write('** Most active date of {} on Whatsapp:**'.format(member))
                 st.pyplot(fx.active_date(member_data))


                 st.write('**When {} is active for chat:**'.format(member))
                 fx.active_time(member_data)
                 st.pyplot(fx.active_time(member_data))


                 st.write('**Day wise distribution of messages for {}:**'.format(member))
                 st.plotly_chart(fx.day_wise_count(member_data))


                 st.write('**Number of messages as times move on**')
                 st.plotly_chart(fx.num_messages(member_data))


    except Exception as e:
        print(e)
        st.write('Please upload your file (.txt file only! file limit-200MB)')




st.sidebar.markdown(
    """
         ** About  Ndu Jude**
  
         ** Data Scientist / Physicist** 
  
  
         """
)


st.sidebar.markdown("[![lets connect](https://forthebadge.com/images/badges/Jesus-Saves.svg)](https://www.linkedin.com/in/jude-chukwuebuka-78ab38175/)")
st.sidebar.markdown("[![Twitter](https://forthebadge.com/images/badges/Jesus-Saves.svg)](https://www.twitter.com/JudeLeonard13/)")


#st.sidebar.markdown("<a href="https://twitter.com/GiftOjeabulu_">
#  <img src="https://img.shields.io/badge/twitter-%231DA1F2.svg?&style=for-the-badge&logo=twitter&logoColor=white" />
#</a>&nbsp;&nbsp;")

'''
<a href="https://twitter.com/GiftOjeabulu_">
  <img src="https://img.shields.io/badge/twitter-%231DA1F2.svg?&style=for-the-badge&logo=twitter&logoColor=white" />
</a>&nbsp;&nbsp;
<a href="mailto:giftoscart@gmail.com">
  <img src="https://img.shields.io/badge/email-%23D14836.svg?&style=for-the-badge&logo=gmail&logoColor=white" />
</a>&nbsp;&nbsp;
  <a href="https://www.linkedin.com/in/gift-ojabu/">
  <img src="https://img.shields.io/badge/linkedin-%230077B5.svg?&style=for-the-badge&logo=linkedin&logoColor=white" />
</a>&nbsp;&nbsp;

'''








if __name__ == "__main__":
    main()
