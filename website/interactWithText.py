from flask import Blueprint, render_template, request, session

from .testing import get_response_from_query
from .source_utils import load_db_for_user

db = None


def _load_db():
    """Lazy-load vector store from Supabase-backed source."""
    global db
    if db is None:
        user_id = session.get("user_id", "anon")
        db = load_db_for_user(user_id)
    return db
interactWithText = Blueprint('interactWithText', __name__)

@interactWithText.route('/interactWithText', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        query = request.form.get('user_query', "").strip()
        response = get_response_from_query(_load_db(), query, "")
        return render_template('interactWithText.html', response=response)
    

    return render_template('interactWithText.html')                                                      
