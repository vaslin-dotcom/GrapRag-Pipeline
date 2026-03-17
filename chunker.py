from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_txt(txt,chunk_size=500,overlap=100):
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )
    chunks=splitter.split_text(txt)
    return chunks

if __name__=='__main__':
    from loading_txt import extract_txt
    txt=extract_txt('Game+of+Thrones.pdf')
    chunks=chunk_txt(txt)
    print(len(chunks))


