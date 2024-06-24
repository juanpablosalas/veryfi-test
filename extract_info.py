from glob import glob
import json
import re

info_general = ['vendor name','vendor address','bill to name','invoice number','date']
line_item = ['sku','description','quantity','tax_rate','price','total']


def get_ocr_text():
    ocr_text = []
    for file_path in glob('data/processed_documents/*.json'):
        with open(file_path, 'r') as file:
            data = json.load(file)
        ocr_text.append(data['ocr_text'])

    return ocr_text

ocr_text = get_ocr_text()


def extract_info_line_item(line_item):
    """
    Extracts the information per line item as a dict.

    Returns dict with keys sku, description, quantity, tax_rate, price, total.

    """
    rows = re.split('\n+',line_item)
    rows = list(filter(lambda s: len(s)>0, rows))
    table = [re.split('\t+',fil) for fil in rows]
    table_as_list = [i for s in table for i in s]

    quantity = None
    string_basecharge = ''
    for el in table_as_list:
        if bool(re.search('^[\d,]+$',el)):
            string_quantity = el
        if (bool(re.search('\$',el))) and ~(quantity is None):
            if 'ea' in el.lower():
                string_ppsku = el
            else:
                string_basecharge =  el
                break

    quantity = int(string_quantity.replace(',',''))
    ppsku = float(re.findall('([\d,]+\.\d+)',string_ppsku)[0].replace(',',''))
    base_charge = float(re.findall('([\d,]+\.\d+)',string_basecharge)[0].replace(',','')) if len(string_basecharge)>0 else 0
    total = quantity*ppsku +base_charge


    desc = line_item.replace(string_quantity,'').replace(string_basecharge,'').replace(string_ppsku,'').replace('QUANTITY','').replace('CODE NO.','').replace('DESCRIPTION','')
    desc = re.sub('[\n\t]+','',desc)
    return {'sku':None,'description':desc,'quantity':quantity,'tax_rate':None,'price':ppsku,'total':total}


def extract_general_info(text: str):
    """
    Extracts the general information from the processed text i.e. vendor_name, vendor_address, bill_to_name, invoice_number, date.

    Returns:
        A tuple consisting of vendor_name (str), vendor_address (str), bill_to_name (str), invoice_number (int), date (int).
    """

    date = re.findall('([A-Z][a-z]+ \d{1,2}, \d{4})',text)[0]
    invoice = re.findall('PURCHASE ORDER NO. M\s?(\d.+)',text)[0]
    bill_to_name = re.findall('(?:TO:\n)(.+)(?:\t)',text)[0].split('\t')[0]

    vendor_address = re.findall('(?:TO:\n)([\S\s]*\d{5})',text)[0]
    second_column = re.findall('(?:.*\t+)(.*)\n',vendor_address)
    for u in second_column:
        vendor_address = vendor_address.replace(u,'')
    vendor_address = ' '.join(vendor_address.split('\n')[-2:])
    vendor_address = re.findall('(.*?\d{5})',vendor_address)[0]
    vendor_address = re.sub(r'\t+','',vendor_address)


    header = text.split('BILLING')[0]
    vendor_name = header.split('\n')
    vendor_name = [txt.split('\t')[0] for txt in vendor_name if (len(txt.split('\t')[0])>0) and (not bool(re.search(r'\d',txt.split('\t')[0])))]
    vendor_name = ' '.join(vendor_name)

    return vendor_name, vendor_address, bill_to_name, int(invoice), date


def extract_info(text: str):
    """
    Extracts info from the OCR processed text.

    Returns:
        Dictionary with vendor_name (str), vendor_address (str), 
                        bill_to_name (str), invoice_number (int), 
                        date(str), line_items(list of dicts)

    Raises:
        Exception if the word ACCOUNTING CHARGE is not present in the text, indicating it is not in the format of TABC invoice.
    """
    if not 'ACCOUNTING CHARGE' in text:
        raise ValueError("The document does not seem to comply with The American Tobacco Company invoice format.")
    
    k = re.sub('[\u4e00-\u9fff]+','',text)
    vendor_name, vendor_address, bill_to_name, invoice, date = extract_general_info(k)
    
    main = k.split('PRICE')[1].split('ACCOUNTING CHARGE')[0]
    line_item = [extract_info_line_item(main)]

    return {'vendor_name':vendor_name,'vendor_address':vendor_address,'bill_to_name':bill_to_name,'invoice_number':invoice,'date':date,'line_items':line_item}

for t in ocr_text:
    try:
        ans = extract_info(t)
        print(ans)
    except ValueError as e:
        print(e)

