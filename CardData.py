import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image                
import pandas as pd
import numpy as np
import re 
import io
import sqlite3


#image to text
def i_t_i(path):
    input_image=Image.open(path)

    #image to array format
    image_arr=np.array(input_image)

    reader=easyocr.Reader(['en'])        #used to read in language 
    text=reader.readtext(image_arr, detail=0) #by giving 0 means it will remove all the values and provide on the text

    return text, input_image

# creating dictionary to read the data 
def extract_text(texts):
    extract_dict={"Name":[], "Designation":[], "Company Name":[], "Contact":[], "Email":[],"Web Site":[],
                  "Address":[], "Pincode":[]}
    
    extract_dict["Name"].append(texts[0])          #should not give = while appending the data in variable
    extract_dict["Designation"].append(texts[1])

    for i in range(2,len(texts)):
        if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and '-' in texts[i]):                                        # +is used tyo choose the contact no. -
            extract_dict["Contact"].append(Text_image[i])

        elif "@" in texts[i] and ".com"in texts[i]:
            extract_dict["Email"].append(texts[i])

        elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i] :
            small=texts[i].lower()
            extract_dict["Web Site"].append(small)

        elif "TamilNadu" in texts[i] or  "Tami lNadu" in texts[i] or texts[i].isdigit():
            extract_dict["Pincode"].append(texts[i])

        elif re.match(r'^[A-Za-z]',texts[i]):
            extract_dict["Company Name"].append(texts[i])

        else:
            remove_colon=re.sub(r'[,;]','',texts[i])
           # extract_dict["Address"].append(texts[i])    
            extract_dict["Address"].append(remove_colon)   

    for key,value in extract_dict.items():
        #print(key,":",value, len(value))
        if len(value)>0:
            concadenate=" ".join(value)  
            extract_dict[key] = [concadenate]  
            #print(concadenate)    

        else:
            value="NA"
            extract_dict[key] = [value]

    #print (extract_dict)
    return extract_dict        


#streamlit Part

st.set_page_config(layout="wide")
st.title("Extracted Business Card Data With 'OCR'")

with st.sidebar:

    select=option_menu("Main Menu", ["Home","Upload & Modify", "Delete"])

if select== "Home":
        pass

elif select== "Upload & Modify":

        image=st.file_uploader("Please Upload the File", type=["png", "jpg", "jpeg"])                   # Indentation error IF

        if image is not None:
             st.image(image,width=300)

             Text_image,input_image =i_t_i(image)                                                        #T(caps) is an variable                                
             
             text_dict=extract_text(Text_image)

             if text_dict:
                  st.success("Data is Extracted")
             tdf=pd.DataFrame(text_dict)

            #  st.dataframe(df)
# converting image to bytes

             img_bytes=io.BytesIO()                           #need to pass the image file
             input_image.save(img_bytes, format="PNG")                                #input_image is the name  to call 

            #to get data from bytes format 
             img_data=img_bytes.getvalue()
            # img_data

#Dictonary
             data={"Image":[img_data]}

# dataframe

             bdf=pd.DataFrame(data)
            #bdf1

             con_df=pd.concat([tdf,bdf],axis=1)
             st.dataframe(con_df)

#Button
             button1 = st.button("Save", use_container_width=True)
             if button1 :                 

                mydb=sqlite3.connect("bizcardx_db")
                cursor=mydb.cursor()


#############################table Creation                
# while using sqlite3 all the keywords should be in caps
                
                table_query= '''CREATE TABLE IF NOT EXISTS bizcard_details (
                                name VARCHAR(255),
                                Designation VARCHAR(255),
                                Company_Name VARCHAR(255),
                                Contact VARCHAR(255),
                                Email VARCHAR(255),
                                Web_Site TEXT,
                                Address TEXT,
                                Pincode VARCHAR(255),
                                image TEXT )'''

                cursor.execute(table_query)

                mydb.commit()

                #insert data

                insert_query='''INSERT INTO bizcard_details(name, Designation, Company_Name, Contact, Email, Web_Site, Address, Pincode,image)
                                                            values(?,?,?,?,?,?,?,?,?)'''

                datas = con_df.values.tolist()[0]    
                cursor.execute(insert_query, datas)  # Execute the insert query with the data
                mydb.commit()  

                st.success("Data Uploaded Successfully")

        method= st.radio("Select the method", ["none","Show","modify"])

    #if you are getting an error while running the dataframe. using none method

        if method == "none":
             st.write("")

        if method == "Show":

            mydb=sqlite3.connect("bizcardx_db")
            cursor=mydb.cursor()

           #select data

            select_query = "SELECT * FROM bizcard_details"

            cursor.execute(select_query)
            table=cursor.fetchall()
            mydb.commit()


            table_df=pd.DataFrame(table, columns=("name", "Designation", "Company_Name", "Contact", "Email", "Web_Site", "Address", "Pincode","image"))  
            st.dataframe(table_df)

   
elif select=="Delete":
        pass
