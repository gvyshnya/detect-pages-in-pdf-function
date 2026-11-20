import requests
import datetime as dt

if __name__ == "__main__":
    start_time = dt.datetime.now()
    print("Started at ", start_time)

    pdf_web_api_url = 'https://europe-west1-lorelee-keep-312708.cloudfunctions.net/detect-pages-in-pdf'

    payload = {
	    "path": "gs://xyz-pdf-reports/poc/Geschaeftsbericht_2020_e.pdf",
        "search_phrase": "EBITDA",
        "max_number_of_pages": "1"
    }

    headers = {
        "Content-Type": "application/json",
    }
    
    response = requests.request("POST", pdf_web_api_url, json=payload, headers=headers)

    print(response.text)
    print('------------------------------------------------')
    print('We are done. That is all, folks!')
    finish_time = dt.datetime.now()
    print("Finished at ", finish_time)
    elapsed = finish_time - start_time
    print("Elapsed time: ", elapsed)