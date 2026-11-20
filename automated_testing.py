import pandas as pd
import json
import os
import requests
import datetime as dt
import ast


folder = 'data'
# excel_file = os.listdir('data')[0]
# excel_file_path = '/'.join([folder, excel_file])
json_path = "data/testing_page_detection.json"

if __name__ == "__main__":
    start_time = dt.datetime.now()
    print("Started at ", start_time)

    pdf_web_api_url = 'https://europe-west1-lorelee-keep-312708.cloudfunctions.net/detect-pages-in-pdf'

    f = open(json_path)
    test_data = json.load(f)
    report_data = []
    for test_case in test_data:
        gs_path = '/'.join(["gs://xyz-pdf-reports/poc", test_case["report"]])
        payload = {
	        "path": gs_path,
            "search_phrase": test_case["label"],
            "max_number_of_pages": test_case["max_pages"]
        }
        headers = {
            "Content-Type": "application/json",
        }

        response = requests.request("POST", pdf_web_api_url, json=payload, headers=headers)
        response_data = ast.literal_eval(response.text)
    
        print('REQUEST:')
        print(payload)
        print('RESPONSE:')
        print(response_data)
  
        test_data_list = ast.literal_eval(test_case['pages'])
        file = test_case['report']
    
        result = False
        if test_data_list == response_data:
            result = True
            print('Test passed for {}'.format(file))
        else:
            print('Test failed for {}'.format(file))
            print('Expected output: {}'.format(test_case['pages']))
            print('Recieved: {}'.format(response.text))

    
        # create report data 
        report_dict = test_case
        report_dict['output'] = response.text
        report_dict['passed'] = result
        report_data.append(report_dict)

    finish_time = dt.datetime.now()
    # compose report name with timestamp
    report_name = 'page_detection_test_report_{}.csv'.format(finish_time.strftime("%Y-%m-%d_%H-%M-%S"))
    report_path = 'data/{}'.format(report_name)
    # save report
    report_df = pd.DataFrame(report_data)
    report_df.to_csv(report_path, index=False)
    
    print("DONE at ", finish_time)
    elapsed = finish_time - start_time
    print("Elapsed time: ", elapsed)
