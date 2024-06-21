from veryfi import Client
from glob import glob
import json
import os
import re


client_id = 'vrfRLHOgd36OHTcs1oSrWWpl8FRR1N8BOvvThnk'
client_secret = '08Bi0LBOFZRkfJySPFl0cLPimm03e3p7e6ZTd3S8JrB4iXICHXvig2eAyrOwOyjj07wxOosSwRZWHkY4IPCI21HYhu9umXKj5b2vW8ZANViHdW5CKr77rGueizKbDYIw'
username = 'juanp.salas'
api_key = 'e579f6549d06224cd0d8b72c854469e4'

categories = ['Advertising & Marketing']


for file_path in glob('data/documents_to_process/*'):
    veryfi_client = Client(client_id, client_secret, username, api_key)
    response = veryfi_client.process_document(file_path, categories=categories)
    print('-'*30)
    print(f'Information for {file_path} was extracted succesfully.')

    new_file_path = re.sub('(\..*)','.json',file_path)
    new_file_path = re.sub('(documents_to_process)','processed_documents',new_file_path)
    with open(new_file_path, 'w') as file:
        json.dump(response, file, indent=4)

    print(f'Information for {file_path} was succesfully saved as a JSON in {new_file_path}')