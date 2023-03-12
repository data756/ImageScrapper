from flask import Flask,render_template,request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
import logging
import pymongo
import os

logging.basicConfig(filename="ImageScrapper.log",level=logging.INFO)

app=Flask(__name__)

@app.route("/", methods=['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review",methods=['GET','POST'])
def index():
    if request.method=='POST':
        try:
            input_query=request.form['content']
            save_directory=os.getcwd()+f"/{input_query}_images"
            logging.info("Creating the working directory for storing image")
            if not os.path.exists(save_directory):
                os.makedirs(save_directory,mode=0o777)
                logging.info(f"new directory is created at {save_directory} with 0o777 permission")
            param_query=input_query.replace(" ","+")
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
            image_search_url=f"https://www.google.com/search?q={param_query}&sxsrf=AJOqlzUDwlAfT3oEP37VZQzo3twoaqIM2Q:1678615119132&source=lnms&tbm=isch&sa=X&ved=2ahUKEwikpY_PkNb9AhV17zgGHRBEDU4Q_AUoA3oECAIQBQ&biw=1846&bih=948&dpr=1"
            logging.info(f"Image Search URL is {image_search_url}")
            response=requests.get(image_search_url)
            logging.info(f"Response Received from the url is {response}")
            soup=BeautifulSoup(response.content,"html.parser")
            image_tags=soup.find_all("img")
            logging.info(f"sourced all the image tags")
            del image_tags[0]
            img_data=[]
            for index,image_tag in enumerate(image_tags):
                image_url=image_tag['src']
                logging.info(f"image url is:- {image_url}")
                image_data=requests.get(image_url).content
                mydict={
                    "Index":index,
                    "ImageData":image_data
                }
                logging.info("Appending the dictionary data into list")
                img_data.append(mydict)
                try:
                    with open(os.path.join(save_directory,f"{input_query}_{image_tags.index(image_tag)}.jpg"),"wb") as f:
                        f.write(image_data)
                except FileExistsError as e:
                    logging.info("File already exists")
                    logging.info(e)
            try:
                client = pymongo.MongoClient(
                    "mongodb+srv://bnmkat1:Mongo1234@pwskills.5tfnndr.mongodb.net/?retryWrites=true&w=majority")
                if client is not None:
                    logging.info("Connection to MongoDB Atlas was successful")
                    database=client['ImageDatabase']
                    collection_name=database['ImageScrapper']
                    logging.info("Connected to the collection ImageScrapper")
                    collection_name.insert_many(img_data)
                    return "Image loaded"
                else:
                    logging.error("Connection was established with the MongoDb")
            except Exception as e:
                logging.info("Some error occured while inserting the data")
                logging.info(e)

        except PermissionError as e:
            logging.info(e)
            return "Something went wrong"

        except Exception as e:
            logging.info(e)
            return "something went wrong"
    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host='0.0.0.0',port=8000)