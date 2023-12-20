from functools import lru_cache
import json
from typing import Optional, List
from sec_edgar_api import EdgarClient
from cache_decorator import Cache
import requests
import logging
from typing import TypedDict


class FilingInfo(TypedDict):
	accessionNumber: str
	filingDate: str
	reportDate: str
	acceptanceDateTime: str
	act: str
	form: str
	fileNumber: str
	filmNumber: str
	items: str
	size: int
	isXBRL: bool
	isInlineXBRL: bool
	primaryDocument: str
	primaryDocDescription: str

class SmartEdgarClient:
	def __init__(self, user_email):
		self.user_email = user_email
		self.user_agent = f"SEC Agent User {user_email}"
		self.client = EdgarClient(user_agent=self.user_agent)

	def toCik(self, cikValue):
		return str(cikValue).zfill(10)
	
	@Cache(cache_path="data/edgar/{function_name}/{cik}.json")
	def get_company_facts(self, cik):
		print(f"get_company_facts for {cik}")
		return self.client.get_company_facts(self.toCik(cik))

	def get_company_facts_usgaap_category_keys(self, cik):
		"""Gets the categories of US GAAP facts for a company"""""
		company_facts = self.get_company_facts(cik)
		us_gaap = company_facts["facts"]["us-gaap"] 
		keys = us_gaap.keys()
		return keys

	def get_company_facts_usgaap_value(self, cik, usgaap_category, units='USD', fy = None):
		"""Gets the value of a US GAAP fact for a company"""""
		company_facts = self.get_company_facts(cik)
		value = company_facts["facts"]["us-gaap"][usgaap_category]["units"][units]
		value = value if fy is None else [item for item in value if item.get('fy') == fy]
		return value


	@Cache(cache_path="data/edgar/{function_name}/{cik}.json")
	def get_submissions(self, cik):
		print(f"get_submissions for {cik}")
		return self.client.get_submissions(self.toCik(cik))

	def get_submission_filings(self, cik, forms: Optional[List[str]] = None, filing_date_min = None) -> List[FilingInfo]:
		"""Gets the filings for a company"""""
		submissions = self.get_submissions(cik)
		recent_filings = submissions["filings"]["recent"]
		filings: List[FilingInfo] = [{key: recent_filings[key][i] for key in recent_filings} for i in range(len(next(iter(recent_filings.values()))))]
		filings = filings if forms is None else [filing for filing in filings if filing['form'] in forms]
		filings = filings if filing_date_min is None else [filing for filing in filings if filing['filingDate'] >= filing_date_min]
		return filings

	@Cache(cache_path="data/edgar/{function_name}/{accession_number}_{primary_document}.json")
	def get_edgar_filing(self, accession_number: str, primary_document: str, cik_number: str):
		"""Gets a filing for a company"""""
		# cik_number = str(int(accession_number.split('-')[0]))
		formatted_accession_number = accession_number.replace('-', '')
		url = f"https://www.sec.gov/Archives/edgar/data/{cik_number}/{formatted_accession_number}/{primary_document}"
		logging.info(f"get_edgar_filing for {accession_number} from {url}")
		with requests.get(url, headers={'User-Agent':self.user_agent}) as response:
			if response.status_code == 404:
				raise Exception(f"Not found error getting filing {accession_number}/{primary_document}")
			if response.status_code != 200:
				raise Exception(f"Error getting filing {accession_number}; status code: {response.status_code}, response: {response.text}")
			logging.info(f"get_edgar_filing for {accession_number} from {url} response type: {response.headers['content-type']} length: {len(response.text)}")
			return response.text
