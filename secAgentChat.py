import os
from llama_index import StorageContext, VectorStoreIndex, load_index_from_storage
from SecFilingReader import SecFilingReader
import dotenv
import logging
import sys

from utils import get_env_var

if __name__ == "__main__":
	# Set up env vars
	dotenv.load_dotenv()
	open_api_key = get_env_var('OPENAI_API_KEY')
	user_email = get_env_var('USER_EMAIL')

	logging.basicConfig(stream=sys.stdout, level=logging.INFO)
	logging.getLogger("pyrate_limiter").setLevel(logging.WARNING)

	logging.getLogger().handlers.clear()
	logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

	storage_path = "./storage"
	if not os.path.exists(storage_path):
		# load the documents and create the index
		print("Creating index")
		documents = SecFilingReader(user_email=user_email).load_data(cik="0000789019", filing_date_min="2010-01-01", forms=["10-K", "10-Q", "8-K", "20-F"])
		index = VectorStoreIndex.from_documents(documents)
		# store it for later
		print("Storing index")
		index.storage_context.persist(persist_dir=storage_path)
	else:
		# load the existing index
		storage_context = StorageContext.from_defaults(persist_dir=storage_path)
		index = load_index_from_storage(storage_context)
		print("Loaded index from storage")

	engine = index.as_chat_engine()

	print("Welcome to the SEC Chatbot. Type 'exit' to quit.")
	while True:
		query = input("Enter query: ")
		if (query == "exit"):
			break
		results = engine.chat(query)
		print(results)
		# print(results[0].document.text)



