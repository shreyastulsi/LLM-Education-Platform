from flask import Blueprint, render_template, request, Flask
import os





handleUpload = Blueprint('handleUpload', __name__)

@handleUpload.route('/handleUpload', methods=['GET','POST'])
def get_file():
    
    if request.method == 'POST':
        
        if 'pdf_file' in request.files and request.files['pdf_file'].filename != '':
            file = request.files['pdf_file']
            file.save('/Users/shreyastulsi/Desktop/LangchainProfessional/experiments/educationGPT/website/currfile.pdf')
            if os.path.exists("/Users/shreyastulsi/Desktop/LangchainProfessional/experiments/educationGPT/website/ytlink.txt"):
                os.remove("/Users/shreyastulsi/Desktop/LangchainProfessional/experiments/educationGPT/website/ytlink.txt")
            return render_template("studyMaterialGen.html")
            
        else:
            youtube_link=request.form['youtube_link']
            with open("/Users/shreyastulsi/Desktop/LangchainProfessional/experiments/educationGPT/website/ytlink.txt", "w") as file:
                file.write(youtube_link)
            if os.path.exists("/Users/shreyastulsi/Desktop/LangchainProfessional/experiments/educationGPT/website/currfile.pdf"):
                os.remove("/Users/shreyastulsi/Desktop/LangchainProfessional/experiments/educationGPT/website/currfile.pdf")
            return render_template("studyMaterialGen.html")
            
    
    return render_template("handleUpload.html")