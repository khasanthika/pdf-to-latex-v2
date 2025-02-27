import os
from flask import Flask, request, render_template
import pdfplumber

app = Flask(__name__)

def create_latex_table(table):
    """
    Convert a table (list of lists) into a simple LaTeX tabular environment.
    Assumes all columns are left-aligned. Adjust formatting as needed.
    """
    if not table or not table[0]:
        return ""
    num_cols = len(table[0])
    latex = "\\begin{tabular}{" + "l" * num_cols + "}\n"
    latex += "\\toprule\n"
    for row in table:
        # Sanitize and join cells, ensuring LaTeX special characters are escaped if needed.
        row_cells = " & ".join(cell.replace('&', '\\&') if cell else '' for cell in row)
        latex += row_cells + " \\\\\n"
    latex += "\\bottomrule\n\\end{tabular}\n"
    return latex

def pdf_to_latex(pdf_file):
    """
    Process the PDF file, extract text, tables, and images,
    then wrap everything into a LaTeX document.
    """
    extracted_content = ""
    image_counter = 0
    image_dir = "static/extracted_images"
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    
    # Open PDF using pdfplumber
    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            # Extract text (this should include math symbols and formulas if they are text)
            text = page.extract_text() or ""
            extracted_content += text + "\n\n"
            
            # Extract tables and convert them to LaTeX
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    latex_table = create_latex_table(table)
                    extracted_content += latex_table + "\n\n"
            
            # Extract images from the page, if any.
            # Note: pdfplumber can detect image objects. Here we try to save them.
            for image in page.images:
                image_counter += 1
                # Define the image path; we assume PNG format for simplicity.
                image_path = os.path.join(image_dir, f"page{page_num}_img{image_counter}.png")
                # Crop image using bounding box coordinates
                # (x0, top, x1, bottom) from the image dict.
                cropped = page.crop((image["x0"], image["top"], image["x1"], image["bottom"])).to_image()
                cropped.save(image_path, format="PNG")
                # Add LaTeX code to include the image.
                # Adjust width/scale as needed.
                extracted_content += (
                    "\\begin{figure}[h]\n"
                    f"\\includegraphics[width=\\linewidth]{{{image_path}}}\n"
                    "\\end{figure}\n\n"
                )
    
    # Wrap all extracted content in a LaTeX document
    latex_document = r"""\documentclass{article}
\usepackage{amsmath, amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\begin{document}
%s
\end{document}""" % extracted_content

    return latex_document

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return "No file provided", 400
        file = request.files['pdf_file']
        if file.filename == '':
            return "No file selected", 400
        
        # Convert PDF to LaTeX with extended extraction features
        latex_content = pdf_to_latex(file)
        return render_template('result.html', latex_content=latex_content)
    
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
