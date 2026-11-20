# Introduction
This repo contains the codebase and assets for *detect-pages-in-pdf* Google Cloud Function.

# Files and Folders

This repo contains the files below

- *main.py* - the main source code module for the cloud function
- *requirements.txt* - the pip-compatible file with the list of the required Python packaged need by the cloud function to run
- *testing.json* - the sample file to demonstrate the input parameters signature for the cloud function
- *automated_testing.json* - ttesting script to process test cases from excel format     
- *README.md* - this README document

# Input and Output Parameters

It takes the following input parameters 
- *str* the path to the pdf report file uploaded to a GCP bucket (in the format of 'gs://your_bucket_name/path/to/your/file.pdf' )
- *str* the search keyword/phrase to lookup within the pdf document pages with the tabular content
- *str* the number of pages to return in the search results (the string will contain digits only, and it will determine the number of elements in the output list with the page numbers - see below)

It returns the *list* of page numbers matching the criteria (casted to JSON)

*Note:* such a list of pages can be then passed to *parse-pdf-table* Google Cloud Function to extract the content of the tables in the respective pages of the pdf report document
