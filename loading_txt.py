from pypdf import PdfReader

def extract_txt(file):
    reader=PdfReader(file)
    txt=''
    for page in reader.pages[1:]:
        extracted_txt=page.extract_text()
        if page:
            txt+=extracted_txt
    return txt

if __name__=='__main__':
    file='Game+of+Thrones.pdf'
    txt=extract_txt(file)
    print(txt[:300])