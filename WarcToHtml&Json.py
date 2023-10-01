import os
import re
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
                ele=exsoup.select('h1')
                if ele:
                    header=ele[0].getText()
                else:
                    header=""
                # Create a dictionary for JSON data
                json_data = {
                    'filename': filename,
                    'header':header,
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
