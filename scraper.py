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


def load_data():
	# Load the data from the website and from the archive
	URL_NEW = 'https://www.studentska-prehrana.si/sl/restaurant'
	URL_OLD = 'https://web.archive.org/web/20220601102110/https://www.studentska-prehrana.si/sl/restaurant'
	df_new = extract_attrs(URL_NEW)
	df_old = extract_attrs(URL_OLD)

	return df_new, df_old


def merge_data(df_new, df_old):
	# Merge the data from the website and from the archive

	# Fix the posid of two restaurants
	df_old.loc[df_old.posid == 2829, 'posid'] = 3191
	df_old.loc[df_old.posid == 2875, 'posid'] = 3205
	# Fix wrong new price of one restaurant
	df_new.loc[df_new.posid == 3071, 'doplacilo'] = 0.0
	df_new.loc[df_new.posid == 3071, 'cena'] = 3.5


	# Merge the data
	df = pd.merge(df_old, df_new, on=['posid'], how='outer', suffixes=('_old', '_new'))

	# Fill the NaN values with the old values
	df.lat_new = df.lat_new.fillna(df.lat_old)
	df.lon_new = df.lon_new.fillna(df.lon_old)
	df.lokal_new = df.lokal_new.fillna(df.lokal_old)
	df.naslov_new = df.naslov_new.fillna(df.naslov_old)
	df.city_new = df.city_new.fillna(df.city_old)
	df.detailslink_new = df.detailslink_new.fillna(df.detailslink_old)
	df['sort-group_new'] = df['sort-group_new'].fillna(df['sort-group_old'])

	# Remove the columns that are not needed, rename the columns and reorder them
	df = df.drop(['lat_old', 'lon_old', 'lokal_old', 'naslov_old', 'city_old', 'detailslink_old', 'sort-group_old'], axis=1)
	df = df.rename(columns={'lat_new': 'lat', 'lon_new': 'lon', 'lokal_new': 'lokal', 'naslov_new': 'naslov', 'city_new': 'city', 'detailslink_new': 'detailslink', 'sort-group_new': 'sort-group', 'cena_old': 'cena_old', 'cena_new': 'cena', 'doplacilo_old': 'doplacilo_old', 'doplacilo_new': 'doplacilo'})
	df = df[['lokal', 'naslov', 'city', 'cena', 'cena_old', 'doplacilo', 'doplacilo_old', 'lat', 'lon', 'posid', 'detailslink', 'sort-group']]

	# Calculate the differences
	df['cena_diff'] = df.cena - df.cena_old
	df['doplacilo_diff'] = df.doplacilo - df.doplacilo_old
	df['cena_diff_percent'] = df.cena_diff / df.cena_old * 100
	df['doplacilo_diff_percent'] = df.doplacilo_diff / df.doplacilo_old * 100

	return df


if __name__ == '__main__':
	df_new, df_old = load_data()
	df = merge_data(df_new, df_old)
	print(df.head())
	print(f'{len(df)} restaurants')
	# saves the data to a json file
	df.to_json('data/restavracije.json', orient='records')
	# saves the data to a csv file
	df.to_csv('data/restavracije.csv', index=False)