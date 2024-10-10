from fpdf import FPDF
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import tempfile
import os

def custom_response(question, answer):
    if question == "headphone_type":
        return ""  

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

    return f"{question}: {answer}"  


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




def add_poppins_font(pdf):
    pdf.add_font("Poppins", "", "Poppins-Regular.ttf", uni=True)
    pdf.set_font("Poppins", size=11)


def generate_decibel_graph(decibel_levels):

    frequencies = list(decibel_levels.keys())
    levels = list(decibel_levels.values())


    freqs = [float(f.split()[0].replace('kHz', '')) for f in frequencies]
    labels = frequencies
    

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(freqs, levels, color='blue', s=100, edgecolor='black', zorder=5)
    

    ax.plot(freqs, levels, color='blue', linestyle='-', linewidth=2, zorder=1)
    

    ax.set_xlim(min(freqs) - 0.5, max(freqs) + 0.5)
    ax.set_ylim(min(levels) - 10, max(levels) + 10)
 
    ax.grid(True, which='both', linestyle='--', linewidth=0.7, alpha=0.7)


    ax.set_title("Audiogram", fontsize=14)
    ax.set_xlabel("Frequency (kHz)", fontsize=12)
    ax.set_ylabel("Decibel Level (dB)", fontsize=12)
    

    for i, txt in enumerate(labels):
        ax.annotate(txt, (freqs[i], levels[i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=9)


    plt.xticks(rotation=45)

    image_stream = BytesIO()
    plt.savefig(image_stream, format='png', bbox_inches='tight')
    image_stream.seek(0)  
    plt.close()  

    return image_stream
    

def generate_dynamic_pdf(data, decibel_levels):
    pdf = FPDF()
    pdf.add_page()
    add_poppins_font(pdf)  

   
    pdf.set_xy(12, 65)  
    pdf.cell(0, 10, txt=f"Full Name: {data['full_name']}")
    pdf.set_xy(80, 65)  
    pdf.cell(0, 10, txt=f"Age: {data['age']}")
    pdf.set_xy(110, 65)  
    pdf.cell(0, 10, txt=f"Sex: {data['sex']}")
    pdf.set_xy(12, 75)  
    pdf.cell(0, 10, txt=f"Contact: {data['contact']}")

    headphone_type_answer = data.get('answers', {}).get('headphone_type', '')
    if headphone_type_answer:
        response_text = custom_response('Instrument', headphone_type_answer)
        pdf.set_xy(140, 65)  
        pdf.cell(0, 10, txt=response_text)

   
    y_position = 98  
    pdf.set_font("Poppins", size=10)
    max_width = 180  
    for question, answer in data.get('answers', {}).items():
       
        response_text = custom_response(question, answer)
        lines = wrap_text(response_text, pdf, max_width)
        for line in lines:
            pdf.set_xy(12, y_position)
            pdf.cell(0, 10, txt=line)
            y_position += 7 

   
    decibel_image = generate_decibel_graph(decibel_levels)

    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image_file:
        temp_image_file.write(decibel_image.getvalue())
        temp_image_file_path = temp_image_file.name
    
    pdf.image(temp_image_file_path, x=10, y=y_position + 10, w=150, h=100)

    
    os.remove(temp_image_file_path)

    
    pdf_output = BytesIO(pdf.output(dest='S').encode('latin1'))  
    pdf_output.seek(0)

    return pdf_output


def merge_with_template(template_path, data, decibel_levels):
    
    template_pdf = PdfReader(template_path)
    template_page = template_pdf.pages[0]

   
    dynamic_pdf = generate_dynamic_pdf(data, decibel_levels)

    
    dynamic_reader = PdfReader(dynamic_pdf)
    dynamic_page = dynamic_reader.pages[0]

   
    writer = PdfWriter()

   
    template_page.merge_page(dynamic_page)
    writer.add_page(template_page)

    
    output_filename = "final_report.pdf"
    with open(output_filename, "wb") as output_pdf:
        writer.write(output_pdf)

    print(f"Generated {output_filename}")
    return output_filename
