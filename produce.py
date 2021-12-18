def main():

    import pandas as pd
    import requests
    import lxml
    from bs4 import BeautifulSoup
    from time import sleep
    from kafka import KafkaProducer
    import time
    from time import sleep
    import numpy as np
    import json
    from json import loads
    from json import dumps
    from kafka import KafkaProducer
    from pymongo import MongoClient
    

    #initialize the variables to store property information
    property_desc = []
    property_price = []
    property_location = []
    property_beds = []
    property_baths = []

    #initialize the mongo database connection
    my_client = MongoClient()
    db = my_client.scrapeCollection
    posts = db.posts

    #running kafka locally
    my_producer3 = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer = lambda x:dumps(x).encode('utf-8')  
    )

    #scrape the first page of the website only
    for page in range(1,2):

        url = 'https://www.property24.co.ke/1-bedroom-properties-to-rent-in-nairobi-p95?Bathrooms=1&PropertyTypes=houses%2capartments-flats%2ctownhouses&Page=' + str(page)
        html_text = requests.get(url).text
        soup = BeautifulSoup(html_text, 'lxml')
        properties = soup.find_all('div', class_='pull-left sc_listingTileContent')

        for properties in properties:

            property_desc = properties.find('div', class_='sc_listingTileArea').text.replace('\r','').replace('\n','')
            property_price = properties.find('span').text.replace(' ','').replace('KSh','').replace('\r','').replace('\n','')
            property_location = properties.find('div', class_='sc_listingTileAddress primaryColor').text.replace('\r','').replace('\n','').replace(' ','')
            property_beds = properties.find('div', class_='sc_listingTileIcons').text.split()[0].replace(' ','')
            property_baths = properties.find('div', class_='sc_listingTileIcons').text.split()[1].replace(' ','')

            print(f"""
            Property Title: {property_desc}
            Property Price: {property_price}
            Property Location: {property_location}
            Property Bedrooms: {property_beds}
            Property Bathrooms: {property_baths}

            """)

            print('')

            data2 = {
                'Property Title':[property_desc],
                'Property Price':[property_price],
                'Property Location':[property_location],
                'Property Bedrooms':[property_beds],
                'Property Bathrooms':[property_baths]
            }

            df = pd.DataFrame(data2)
            
            #json object, kafka can't recieve dataframes
            result = df.to_json(orient=None)
            
            #scrapeTut10 is the kafka topic in use
            my_producer3.send('scrapeTut10', value=result)

            #mongodb used as a data lake
            posts.insert_one(data2)

            #timer to avoid getting blocked from the website
            time_wait = 5
            time.sleep(time_wait * 1)

if __name__ == '__main__':
    main()
