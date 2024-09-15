from fpdf import FPDF

def generate_pdf_report(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Title
    pdf.cell(200, 10, txt="Hearing Test Report", ln=True, align='C')
    pdf.ln(10)

    # User Info
    pdf.cell(200, 10, txt=f"Full Name: {data['full_name']}", ln=True)
    pdf.cell(200, 10, txt=f"Age: {data['age']}", ln=True)
    pdf.cell(200, 10, txt=f"Contact: {data['contact']}", ln=True)
    pdf.ln(10)

    # Test Results
    for question, answer in data['answers'].items():
        pdf.cell(200, 10, txt=f"{question}: {answer}", ln=True)

    # Save PDF
    filename = "report.pdf"
    pdf.output(filename)
    print(f"Generated {filename}")
    return filename
