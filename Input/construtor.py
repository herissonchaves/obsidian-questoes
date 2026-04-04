import sys
import os
import shutil

def extract_docx(file_path, base_dir):
    try:
        import docx2txt
    except ImportError:
        os.system(f"{sys.executable} -m pip install docx2txt")
        import docx2txt

    img_dir = os.path.join(base_dir, "extracted_images")
    os.makedirs(img_dir, exist_ok=True)
    text = docx2txt.process(file_path, img_dir)
    return text

def extract_pdf(file_path, base_dir):
    try:
        import fitz # PyMuPDF
    except ImportError:
        os.system(f"{sys.executable} -m pip install PyMuPDF")
        import fitz

    doc = fitz.open(file_path)
    text = ""
    img_dir = os.path.join(base_dir, "extracted_images")
    os.makedirs(img_dir, exist_ok=True)
    
    img_count = 0
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
        for img in page.get_images(full=True):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image["image"]
            ext = base_image["ext"]
            img_count += 1
            with open(os.path.join(img_dir, f"image_{page_num}_{img_count}.{ext}"), "wb") as f:
                f.write(img_bytes)
    return text

def extract_any(file_path):
    base_dir = os.path.dirname(os.path.abspath(file_path))
    ext = file_path.lower().split('.')[-1]
    
    print(f"Extracting {file_path}...")
    if ext == 'docx':
        text = extract_docx(file_path, base_dir)
    elif ext == 'pdf':
        text = extract_pdf(file_path, base_dir)
    else:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
            
    out_path = os.path.join(base_dir, "extracted_text.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Extraction complete. Text saved to {out_path}.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python construtor.py <file>")
        sys.exit(1)
    extract_any(sys.argv[1])
