import numpy as np
from bs4 import BeautifulSoup
import requests
import pandas as pd


def extract_attrs(url):
	# Get the HTML from the website
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')

	# Find all div elements with the class 'restaurant-row'
	divs = soup.find_all('div', class_=['restaurant-row'])

	# Iterate over the div elements and extract the attributes
	data = []
	for div in divs:
		attrs = div.attrs
		del attrs['class']
		data.append(attrs)

	# Create a Pandas DataFrame from the data list
	df = pd.DataFrame(data)
	# Remove the prefix 'data-' from the column names
	df = df.rename(columns={col: col.replace('data-', '') for col in df.columns})

	# Convert the types of the columns
	df.cena = df.cena.str.replace(',', '.').astype(float)
	df.doplacilo = df.doplacilo.str.replace(',', '.').astype(float)
	df.lat = df.lat.astype(float)
	df.lon = df.lon.astype(float)
	df.posid = df.posid.astype(int)
	df.lokal = df.lokal.astype('string')
	df.naslov = df.naslov.astype('string')
	df.city = df.city.astype('string')
	df.detailslink = df.detailslink.astype('string')
	
	return df