import os
import re
from datetime import datetime
import json
import gzip
import bs4
from warcio.archiveiterator import ArchiveIterator

files='files'
for warc_name in os.listdir(files):
    year=warc_name.split('-')
    year=year[2]
    year=year[:4]
    # Create a folder to store the HTML and JSON files
    output_folder = year
    os.makedirs(output_folder, exist_ok=True)


    output_folder_json = f'{year}_json'
    os.makedirs(output_folder_json, exist_ok=True)
    # Open WARC file
    with gzip.open('CC-NEWS-20160826124520-00000.warc.gz', 'rb') as warc_file:
        # Create ArchiveIterator
        for record in ArchiveIterator(warc_file):
            # Check if the record is a response containing HTML content
            if record.rec_type == 'response' and record.http_headers.get_header('Content-Type').startswith('text/html'):
                # Extract the raw content
                raw_content = record.content_stream().read()

                # Attempt to decode the content using different encodings
                encodings = ['utf-8', 'latin-1']  # Add more encodings if needed
                html_content = None
                encoding_used = None
                for encoding in encodings:
                    try:
                        html_content = raw_content.decode(encoding)
                        encoding_used = encoding
                        break
                    except UnicodeDecodeError:
                        pass

                if html_content is None:
                
                    raise Exception(f"Content decoding failed.")

                # Generate a valid filename using the WARC record ID
                record_id = record.rec_headers.get_header('WARC-Record-ID')
                filename = re.sub(r'[:<>]', '_', record_id) + '.html'
                html_filepath = os.path.join(output_folder, filename)

                # Save the HTML content to a file
                with open(html_filepath, 'w', encoding='utf-8') as html_file:
                    html_file.write(html_content)

                print(f"Saved HTML file: {filename}")
                exsoup=bs4.BeautifulSoup(html_content,'html.parser')
                pattern1=r'(\b\d{4}.\d{1,2}.\d{1,2}\b)'
                pattern2=r'(\b\d{1,2}\s\w+\s\d{4}\b)'
                ele=exsoup.select('h1')
                body=exsoup.select('body')
                if body:
                    content=str(body[0].getText())
                if ele:
                    header=ele[0].getText()
                else:
                    header=""
                # Extract date from <meta> tag
                meta_date = exsoup.find('meta', property='article:published_time')
                if meta_date:
                    meta_date = meta_date.get('content')
                match1=re.findall(pattern1,content)
                match2=re.findall(pattern2,content)
                
                
                # Extract date from <time> tag
                time_date = exsoup.find('time')
                if time_date:
                    time_date = time_date.get('datetime')

                # Print the extracted date
                if meta_date:
                     #print('Date from meta tag:', meta_date)
                     meta_date=meta_date[:10]
                     date=meta_date
                     print('meta',date)
                elif time_date:
                    #print('Date from time tag:', time_date)
                    time_date=time_date[:10]
                    date=time_date
                    print('time',date)
                    
                elif  match1:
                    #print(match1[0])
                    date_str=match1[0]
                    try:
                        date_obj = datetime.strptime(date_str, '%Y.%m.%d')
                        formatted_date = date_obj.strftime('%Y-%m-%d')
                        #content = content.replace(date_string, formatted_date)
                        date=formatted_date
                    except ValueError:
                                pass
                elif match2:
                    for match in match2:
                        date_string = match
                        try:
                            date_obj = datetime.strptime(date_string, '%d %B %Y')
                            formatted_date = date_obj.strftime('%Y-%m-%d')
                            #content = content.replace(date_string, formatted_date)
                            date=formatted_date
                        except ValueError:
                                pass
                else:
                    #print('Date not found.')
                    date=""
                try:
                    datetime.strptime(date, "%Y-%m-%d")
                    print(date)
                except ValueError:
                    print("Date not found or not in the correct format (YYYY-MM-DD).")
                # Create a dictionary for JSON data
                json_data = {
                    'filename': filename,
                    'header':header,
                    'publishing_date':date,
                    'record_id': record_id,
                    'content_type': record.http_headers.get_header('Content-Type'),
                    'encoding_used': encoding_used,
                    # Add more fields as needed
                }

                # Generate a valid filename for JSON file
                json_filename = re.sub(r'[:<>]', '_', record_id) + '.json'
                json_filepath = os.path.join(output_folder_json, json_filename)

                # Save JSON data to a file
                with open(json_filepath, 'w', encoding='utf-8') as json_file:
                    json.dump(json_data, json_file, indent=4)
            
                print(f"Saved JSON file: {json_filename}")
