import pandas
import json
import uuid

def excel_to_json(xlsx_path: str, json_path: str):
    # save excel file as json file, using pandas
    excel_data_df = pandas.read_excel(excel_file_path)
    # print(excel_data_df)
    json_str = excel_data_df.to_json(orient='records')
    
    json_data = json.loads(json_str)

    print('Excel Sheet to JSON:')
    print(json_data)
    print('First record')
    print(json_data[0])
    
 

    json_to_write = json.dumps(json_data)
    
    jsonFile = open(json_file_path, "w")
    jsonFile.write(json_to_write)
    jsonFile.close()

    print('saved as', json_file_path)
    
    return 0
json_file_path = 'data/testing_page_detection.json'
excel_file_path = 'data/page_detection_testing.xlsx'

excel_to_json(excel_file_path, json_file_path)
