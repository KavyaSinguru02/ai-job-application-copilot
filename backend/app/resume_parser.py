import pdfplumber
import tempfile

async def extract_resume_text(resume_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        content = await resume_file.read()
        temp.write(content)
        temp_path = temp.name

    text = ""

    with pdfplumber.open(temp_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text