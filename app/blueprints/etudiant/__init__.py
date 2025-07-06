from flask import Blueprint

bp = Blueprint('etudiant', __name__, url_prefix='/etudiant')

from . import routes 