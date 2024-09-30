# Dell Warrany API Retrieval Script

## What is it ?
Example of python script to retrieve Dell Warranty information for a list of servic tags using the Dell API as follow :

<img width="1035" alt="image" src="https://user-images.githubusercontent.com/28600326/225572877-8f3d26bc-fc8b-4a5f-b449-207677317f8e.png">

## Prerequisites
- Dell Tech API access
- Dell API Client ID
- Dell API Client Secret

## Get started
1. Clone or download this repo
```console
git clone https://github.com/deawar/DellAPIPython
```
2. Install required packages
```console
python3 -m pip install -r requirements.txt
```
3. Add a ```.env``` file as follow:
```diff
└── DellAPIPython/
+   ├── .env
    ├── requirements.txt
    └── src/
         └── DellWarrantyAPI.py  
```
4. In the ```.env``` file, add the following variables:
```env
#.env
---
client_secret = " "<your_client_secret>"
client_id = "<your_client_id>"
...

```

5. Now you can run the code by using the following command:
```console
python3 src/DellWarrantyAPI.py -f <your_csv_file.csv> -r <path_and_name_of_output.csv>
```

## Output
The output should be as followed:
```console
File path:  Your_servicetags_file_path.csv
Service tags from file:  [{'serviceTag': 'xxxxxxx'}, {'serviceTag': '2xxxxxx'}, {'serviceTag': '3xxxxxx'},...]
Output written to: Your_File_path_and_filename.csv
```




