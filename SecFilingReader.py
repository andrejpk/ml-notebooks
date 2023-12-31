import asyncio
import logging
from llama_index import Document
from llama_index.readers.base import BaseReader
from typing import Any, Dict, List, Optional, TypedDict
import html2text

from SmartEdgarClient import FilingInfo, SmartEdgarClient


class FilingDocumentRecord(TypedDict):
	filingInfo: FilingInfo
	document: str
	sourceUrl: str

class SecFilingReader(BaseReader):
	"""
	A reader for SEC Edgar filings

	Retrieves data from the SEC Edgar API
	"""
	def __init__(
				self, 
				user_email: str, 
		):
			"""
			Initialize the SecFilingReader object.

			Args:
				user_email (str): The email address of the user.
			"""
			self.edgar_client = SmartEdgarClient(user_email)

			# Set up the event loop
			try:
				self._loop = asyncio.get_running_loop()
			except RuntimeError:
				# If there is no running loop, create a new one
				self._loop = asyncio.new_event_loop()
				asyncio.set_event_loop(self._loop)


	def _load_filing_data(self, cik: str, forms: Optional[List[str]] = None, filing_date_min: Optional[str] = None) -> List[Document]:
		logging.debug(f"Loading filing list for {cik}")
		filings = self.edgar_client.get_submission_filings(cik, filing_date_min=filing_date_min, forms=forms)
		documents = [self._load_filing(data, cik, {'cik': cik}) for data in filings] 
		return [doc for doc in documents if doc is not None]

	def _load_filing(self, filingInfo: FilingInfo, cik_number: str, extra_info: Dict[str, Any]) -> Optional[Document]:
		"""Gets the filing for a filingInfo object"""""
		primary_document = filingInfo["primaryDocument"]
		assession_number = filingInfo["accessionNumber"]
		logging.debug(f"Loading filing {assession_number}/{primary_document}")
		try:
			filing = self.edgar_client.get_edgar_filing(assession_number, primary_document, cik_number)
			return self._generate_document(filingInfo, filing, extra_info=extra_info)
		except Exception as e:
			logging.error(f"Error while loading filing {filingInfo['accessionNumber']}: {e}")
			# raise e
			return None

	def _generate_document(self, filingInfo: FilingInfo, document_content: str, extra_info: Dict[str,Any] = {}) -> Document:
		"""Generates a document for a filingInfo object"""""
		bodyText = html2text.html2text(document_content)
		document = Document(text=bodyText, extra_info=extra_info)
		return document


	def load_data(self, cik: str, forms: Optional[List[str]] = None, filing_date_min = None) -> List[Document]:
		"""Gets the filings for the specified company"""""
		filings = self._load_filing_data(cik, forms, filing_date_min)

		return filings
