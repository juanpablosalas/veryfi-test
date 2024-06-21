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
    filas = re.split('\n+',line_item)
    filas = list(filter(lambda s: len(s)>0, filas))
    table = [re.split('\t+',fil) for fil in filas]
    main = [i for s in table for i in s]

    quantity = None
    string_basecharge = ''
    for el in main:
        if bool(re.search('^[\d,]+$',el)):
            string_quantity = el
        if (bool(re.search('\$',el))) and ~(quantity is None):
            if 'ea' in el.lower():
                string_ppsku = el
            else:
                string_basecharge = el
                break

    quantity = int(string_quantity.replace(',',''))
    ppsku = float(re.findall('([\d,]+\.\d+)',string_ppsku)[0].replace(',',''))
    base_charge = float(re.findall('([\d,]+\.\d+)',string_basecharge)[0].replace(',','')) if len(string_basecharge)>0 else 0
    total = quantity*ppsku +base_charge


    #main = [m for m in main if m not in [string_quantity,string_basecharge,string_ppsku,'QUANTITY','CODE NO.','DESCRIPTION']]
    desc = line_item.replace(string_quantity,'').replace(string_basecharge,'').replace(string_ppsku,'').replace('QUANTITY','').replace('CODE NO.','').replace('DESCRIPTION','')
    desc = re.sub('[\n\t]+','',desc)
    return {'sku':None,'description':desc,'quantity':quantity,'tax_rate':None,'price':ppsku,'total':total}

def extract_general_info(text):
    k = re.sub('[\u4e00-\u9fff]+','',text)
    date = re.findall('([A-Z][a-z]+ \d{1,2}, \d{4})',k)[0]
    invoice = re.findall('PURCHASE ORDER NO. M\s?(\d.+)',k)[0]
    bill_to_name = re.findall('(?:TO:\n)(.+)(?:\t)',k)[0].split('\t')[0]

    vendor_address = re.findall('(?:TO:\n)([\S\s]*\d{5})',k)[0]
    second_column = re.findall('(?:.*\t+)(.*)\n',vendor_address)
    for u in second_column:
        vendor_address = vendor_address.replace(u,'')
    vendor_address = ' '.join(vendor_address.split('\n')[-2:])
    vendor_address = re.findall('(.*?\d{5})',vendor_address)[0]
    vendor_address = re.sub(r'\t+','',vendor_address)

    header = k.split('BILLING')[0]
    vendor_name = header.split('\n')
    vendor_name = [txt.split('\t')[0] for txt in vendor_name if (len(txt.split('\t')[0])>0) and (not bool(re.search(r'\d',txt.split('\t')[0])))]
    vendor_name = ' '.join(vendor_name)

    main = k.split('PRICE')[1].split('ACCOUNTING CHARGE')[0]

    line_item = [extract_info_line_item(main)]

    return {'vendor_name':vendor_name,'vendor_address':vendor_address,'bill_to_name':bill_to_name,'invoice_number':invoice,'date':date,'line_items':line_item}

for t in ocr_text:
    ans = extract_general_info(t)
    print(ans)