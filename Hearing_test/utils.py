from fpdf import FPDF
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import tempfile
import os

def custom_response(question, answer):
    # Your existing custom_response logic
    if question == "headphone_type":
        return ""  # Return an empty string for headphone_type

    if question == "hearing_description":
        if answer == "Poor":
            return "Based on your response, it is advised to seek a detailed hearing evaluation."
        elif answer == "Good":
            return "Your hearing seems to be in good condition. Continue regular check-ups."
        elif answer == "Not Sure":
            return "It is recommended to consult a hearing specialist for further assessment."

    elif question == "conversation_follow":
        if answer == "Always":
            return "It seems that you may be experiencing significant difficulty in following conversations. Consulting a hearing professional could be beneficial."
        elif answer == "Often":
            return "You might have some trouble with conversations. A hearing assessment might help identify any issues."
        elif answer == "Sometimes":
            return "You occasionally find it hard to follow conversations. Monitoring your hearing and consulting with a specialist if necessary is advisable."
        elif answer == "Rarely":
            return "You rarely have trouble with conversations. However, regular hearing check-ups are still recommended."
        elif answer == "Never":
            return "You do not have trouble following conversations. Continue to maintain good hearing health with periodic check-ups."

    elif question == "phone_conversation":
        if answer == "Always":
            return "You might experience significant difficulty with phone conversations. Consulting with a hearing specialist could be useful."
        elif answer == "Often":
            return "You may have frequent trouble with phone conversations. It could be helpful to have your hearing evaluated."
        elif answer == "Sometimes":
            return "You sometimes find phone conversations challenging. Regular hearing assessments and strategies might be beneficial."
        elif answer == "Rarely":
            return "You rarely have issues with phone conversations. Continue with routine hearing check-ups."
        elif answer == "Never":
            return "You do not have trouble with phone conversations. Keep up with periodic hearing health reviews."

    elif question == "high_pitched_sounds":
        if answer == "Always":
            return "Significant difficulty hearing high-pitched sounds. Consult a hearing specialist."
        elif answer == "Often":
            return "Frequent issues with high-pitched sounds. Consider a hearing assessment."
        elif answer == "Sometimes":
            return "Occasional trouble with high-pitched sounds. Regular check-ups may help."
        elif answer == "Rarely":
            return "Rare issues with high-pitched sounds. Periodic assessments recommended."
        elif answer == "Never":
            return "No trouble with high-pitched sounds. Maintain regular check-ups."

    elif question == "noisy_environments":
        if answer == "Always":
            return "You might find it extremely challenging to follow conversations in noisy environments. Seeking advice from a hearing specialist could be beneficial."
        elif answer == "Often":
            return "You frequently have trouble in noisy environments. Consider having your hearing evaluated for potential issues."
        elif answer == "Sometimes":
            return "You sometimes struggle with conversations in noisy settings. Regular hearing assessments might help."
        elif answer == "Rarely":
            return "You rarely have difficulty in noisy environments. Regular hearing check-ups are still advisable."
        elif answer == "Never":
            return "You do not have trouble following conversations in noisy environments. Maintain your hearing health with periodic reviews."

    return f"{question}: {answer}"  # Default response if no match is found

def wrap_text(text, pdf, max_width):
    """Wrap text to fit within a given width in the PDF."""
    lines = []
    words = text.split()
    line = ""

    for word in words:
        test_line = f"{line} {word}".strip()
        pdf.set_font("Poppins", size=10)
        width = pdf.get_string_width(test_line)
        if width > max_width:
            lines.append(line)
            line = word
        else:
            line = test_line

    lines.append(line)
    return lines

# Function to generate the dynamic content on the PDF
def generate_dynamic_pdf(data, decibel_levels):
    pdf = FPDF()
    pdf.add_page()
    add_poppins_font(pdf)  # Use Poppins as the font

    # User Info at specified coordinates
    pdf.set_xy(12, 65)  # Set position for Full Name
    pdf.cell(0, 10, txt=f"Full Name: {data['full_name']}")
    pdf.set_xy(80, 65)  # Set position for Age
    pdf.cell(0, 10, txt=f"Age: {data['age']}")
    pdf.set_xy(110, 65)  # Set position for Sex
    pdf.cell(0, 10, txt=f"Sex: {data['sex']}")
    pdf.set_xy(12, 75)  # Set position for Contact
    pdf.cell(0, 10, txt=f"Contact: {data['contact']}")

    headphone_type_answer = data.get('answers', {}).get('headphone_type', '')
    if headphone_type_answer:
        response_text = custom_response('Instrument', headphone_type_answer)
        pdf.set_xy(140, 65)  # Set position for Headphone Type
        pdf.cell(0, 10, txt=response_text)

    # Test Results
    y_position = 98  # Starting y position for test results
    pdf.set_font("Poppins", size=10)
    max_width = 180  # Maximum width for text wrapping
    for question, answer in data.get('answers', {}).items():
        # Apply custom response logic
        response_text = custom_response(question, answer)
        lines = wrap_text(response_text, pdf, max_width)
        for line in lines:
            pdf.set_xy(12, y_position)
            pdf.cell(0, 10, txt=line)
            y_position += 7  # Move down for next line

    # Generate and add the decibel level graph
    decibel_image = generate_decibel_graph(decibel_levels)

    # Save the BytesIO stream to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image_file:
        temp_image_file.write(decibel_image.getvalue())
        temp_image_file_path = temp_image_file.name
    
    pdf.image(temp_image_file_path, x=10, y=y_position + 10, w=150, h=100)

    # Delete the temporary file after use
    os.remove(temp_image_file_path)

    # Output to a byte stream instead of saving directly
    pdf_output = BytesIO(pdf.output(dest='S').encode('latin1'))  # Convert to a bytes object
    pdf_output.seek(0)

    return pdf_output

# Function to merge the dynamic content with the existing PDF template
def merge_with_template(template_path, data, decibel_levels):
    # Open the PDF template
    template_pdf = PdfReader(template_path)
    template_page = template_pdf.pages[0]

    # Generate the dynamic content PDF
    dynamic_pdf = generate_dynamic_pdf(data, decibel_levels)

    # Read the dynamic content PDF
    dynamic_reader = PdfReader(dynamic_pdf)
    dynamic_page = dynamic_reader.pages[0]

    # Create a writer to combine the PDFs
    writer = PdfWriter()

    # Merge the dynamic page onto the template
    template_page.merge_page(dynamic_page)
    writer.add_page(template_page)

    # Save the merged PDF
    output_filename = "final_report.pdf"
    with open(output_filename, "wb") as output_pdf:
        writer.write(output_pdf)

    print(f"Generated {output_filename}")
    return output_filename
