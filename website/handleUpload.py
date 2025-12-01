from flask import Blueprint, render_template, request, Flask, session
from .supabase_client import upload_bytes, record_source





handleUpload = Blueprint('handleUpload', __name__)

@handleUpload.route('/handleUpload', methods=['GET','POST'])
def get_file():
    user_id = session.get("user_id", "anon")
    
    if request.method == 'POST':
        
        if 'pdf_file' in request.files and request.files['pdf_file'].filename != '':
            file = request.files['pdf_file']
            data = file.read()
            storage_key = upload_bytes(user_id, file.filename, data)
            record_source(user_id, source_type="pdf", storage_path=storage_key)
            return render_template("studyMaterialGen.html")
            
        else:
            youtube_link=request.form['youtube_link']
            record_source(user_id, source_type="youtube", youtube_url=youtube_link)
            return render_template("studyMaterialGen.html")
            
    
    return render_template("handleUpload.html")
