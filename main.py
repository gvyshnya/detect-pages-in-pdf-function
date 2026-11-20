# This cloud function constitutes the Web API for the lookup of the pdf pages with 
#  - (1) tabular data, and
#  - (2) certain keywords (labels) in the page content
# 
# It takes the following input parameters 
# - str the path to the pdf report file uploaded to a GCP bucket 
#   (in the format of 'gs://your_bucket_name/path/to/your/file.pdf' )
# - str the search keyword/phrase to lookup within the pdf document pages with the tabular content
# - str the number of pages to return in the search results (the string will contain digits only, 
#   and it will determine the number of elements in the output list with the page numbers - see below)
#
# It returns the list of page numbers matching the criteria (casted to JSON)

import os
import pandas as pd

import json
from flask import Flask, request, Response

from google.cloud import storage
from io import BytesIO

import fitz

GCP_PROJECT_ID = 'lorelee-keep-312708'

IS_LOCAL = True if os.environ.get("IS_LOCAL", "True").lower() == "true" else False
BQ_PROJECT_ID = os.environ.get("PROJECT_ID", GCP_PROJECT_ID)

# minimum <digit>/<char> rate to consider
DEFAULT_THRESHOLD = 0.09
# minimum length of text at the page, to avoid contacts pages
LENGTH_LIMIT = 900

app = Flask(__name__)

# this function will find all of the pages within the pdf document
# where there is a label keyword to occur
def find_label(pdf_file_path: str, label: str, show=False)->list:

    tokens = pdf_file_path.replace("gs://", "").split('/')

    bucket_name = tokens[0]  # 'xyz-pdf-reports'
    source_blob_name = '/'.join(tokens[1:len(tokens)])

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(source_blob_name)

    mem_area = BytesIO()
    bucket.get_blob(blob_name=source_blob_name).download_to_file(mem_area)

    # mem_area may be one of the Python types bytearray, bytes, io.BytesIO.
    pdf_pages = fitz.open(stream=mem_area, filetype="pdf")
    label_pages = []

    for i in range(len(pdf_pages)):
        text = pdf_pages[i].get_text()
        if label in text:
            label_pages.append(i)
    if show:
        if label_pages:
            print(f'{label} mentioned {len(label_pages)} times in {source_blob_name} at pages:')
            print(label_pages)
        else:
            print(f'No {label} mentioned in {source_blob_name}')
    
    return label_pages

# calculate the relevance rating of each page of the pdf  document
# in terms of its tabular content
def rate_pages(pdf_file_path: str)->list:
    page_dict = []

    tokens = pdf_file_path.replace("gs://", "").split('/')

    bucket_name = tokens[0]  # 'xyz-pdf-reports'
    source_blob_name = '/'.join(tokens[1:len(tokens)])

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(source_blob_name)

    mem_area = BytesIO()
    bucket.get_blob(blob_name=source_blob_name).download_to_file(mem_area)

    # mem_area may be one of the Python types bytearray, bytes, io.BytesIO.
    pdf_pages = fitz.open(stream=mem_area, filetype="pdf")
    for i in range(len(pdf_pages)):
        page_text = pdf_pages[i].get_text()
        page = {
            'num': i,
            'rate': 0,
            'length': len(page_text),
            'text': page_text,
            }
        digits = 0
        for s in page_text:
            if s.isdigit():
                digits+=1
        page['rate'] = digits/(1+len(page_text)-digits) # <num_digits>/<num_chars>
        page_dict.append(page)

    return page_dict

@app.route("/", methods=["POST"])
def detect_pages_with_tables_and_label(request: request):

    # request properties
    request_json = request.get_json(silent=True)
    # expected format of the pdf file path in GCP is as follows
    # gs://[bucket_name]/path/to/file.pdf
    pdf_file_path = request_json.get('path')
    search_phrase = request_json.get('search_phrase')

    number_of_pages_to_return = int(request_json.get('max_number_of_pages'))

    pages_with_label = []
    pages_with_tables_and_label = []

    pages_with_label = find_label(pdf_file_path, search_phrase)

    pages_tabular_rating = rate_pages(pdf_file_path)

    for page in pages_tabular_rating:
        if (page['rate'] > DEFAULT_THRESHOLD) and (page['length'] > LENGTH_LIMIT):
            print('High-rating page details:') 
            print(page['num']) 
            print('Length:', page['length'])
            if page['num'] in pages_with_label:
                pages_with_tables_and_label.append(page)

    output_page_numbers = []
    if len(pages_with_tables_and_label) <= number_of_pages_to_return:
        output_page_numbers = [page['num'] for page in pages_with_tables_and_label]
    else:
        # handle page lists with more then *number_of_pages_to_return* pages in it
        sorted_page_list = sorted(pages_with_tables_and_label, key=lambda k: k['rate'], reverse=True) 
        output_page_numbers = [page['num'] for page in sorted_page_list[0:number_of_pages_to_return]]
    str_json = json.dumps(output_page_numbers)

    return Response(status=200, response=str_json, mimetype='application/json')

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8088, debug=True)
