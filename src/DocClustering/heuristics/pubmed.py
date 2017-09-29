from bs4 import BeautifulSoup
import requests

def get_year(id):
	r = requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id='+str(id))
	html = r.text
	# Setup the BeautifulSoup Parser
	soup = BeautifulSoup(html, 'html.parser')
	year = soup.findAll(attrs={"name" : "PubDate"})
	value = "0000"
	for val in year:
		value = val.text
	return int(value[0:4])
