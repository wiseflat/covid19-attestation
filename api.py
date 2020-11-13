#!/usr/bin/python3
import datetime
import os
import uuid 

from flask import Flask, send_file
from flask_restplus import Api, Resource, fields, reqparse, inputs
from fpdf import FPDF
from werkzeug.utils import cached_property
# from werkzeug.contrib.fixers import ProxyFix
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='covid API', description='API pour générer une attestation de déplacement')

regex_sexe = r'^(H|F)$'
regex_string = r'^[A-Za-zàáâäçèéêëìíîïñòóôöùúûü\s-]{2,50}$'
regex_naissance = r'^([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)\d{4}$'
regex_adresse = r'^[A-Za-zàáâäçèéêëìíîïñòóôöùúûü0-9\s]{2,50}$'
regex_codepostal = r'\d{5}'
regex_motif = r'(Convocation|Missions|Handicap|Santé|Enfants|Famille|Sports et animaux|Travail|Achats)'

parser = reqparse.RequestParser()
parser.add_argument('sexe', type=inputs.regex(regex_sexe), required=True, help='Sexe (H/F)')
parser.add_argument('prenom', type=inputs.regex(regex_string), required=True, help='Prénom')
parser.add_argument('nom', type=inputs.regex(regex_string), required=True, help='Nom de famille')
parser.add_argument('naissance', type=inputs.regex(regex_naissance), required=True, help='Date de naissance')
parser.add_argument('lieu', type=inputs.regex(regex_string), required=True, help='Ville de naissance')
parser.add_argument('adresse', type=inputs.regex(regex_adresse), required=True, help='Adresse')
parser.add_argument('ville', type=inputs.regex(regex_string), required=True, help='Ville')
parser.add_argument('codepostal', type=inputs.regex(regex_codepostal), required=True, help='Code postal')
parser.add_argument('motif', type=inputs.regex(regex_motif), required=True, help='motif')

def document(args):

    date = datetime.datetime.now()

    if(args.sexe == 'H'):
        sexe = ''
        genre = 'M.'
    else:
        sexe = 'e'
        genre = 'Mme'
    if(args.motif == 'Convocation'):
        motif = "Convocation judiciaire ou administrative et pour se rendre dans un service public"
    if(args.motif == 'Missions'):
        motif = "Participation à des missions d'intérêt général sur demande de l'autorité administrative"
    if(args.motif == 'Handicap'):
        motif = "Déplacement des personnes en situation de handicap et leur accompagnant."
    if(args.motif == 'Santé'):
        motif = "Consultations, examens et soins ne pouvant être assurés à distance et l’achat de médicaments."
    if(args.motif == 'Enfants'):
        motif = "Déplacement pour chercher les enfants à l’école et à l’occasion de leurs activités périscolaires"
    if(args.motif == 'Famille'):
        motif = "Déplacements pour motif familial impérieux, pour l'assistance aux personnes vulnérables et précaires ou la garde d'enfants."
    if(args.motif == 'Sports et animaux'):
        motif = "Déplacements brefs, dans la limite d'une heure quotidienne et dans un rayon maximal d'un kilomètre autour du domicile, liés soit à l'activité physique individuelle des personnes, à l'exclusion de toute pratique sportive collective et de toute proximité avec d'autres personnes, soit à la promenade avec les seules personnes regroupées dans un même domicile, soit aux besoins des animaux de compagnie."
    if(args.motif == 'Travail'):
        motif = "Déplacements entre le domicile et le lieu d’exercice de l’activité professionnelle ou un établissement d’enseignement ou de formation, déplacements professionnels ne pouvant être différés , déplacements pour un concours ou un examen."
    if(args.motif == 'Achats'):
        motif = "Déplacements pour effectuer des achats de fournitures nécessaires à l'activité professionnelle, des achats de première nécessité3 dans des établissements dont les activités demeurent autorisées, le retrait de commande et les livraisons à domicile."

    texte = f'''ATTESTATION DE DÉPLACEMENT DÉROGATOIRE

En application du décret n°2020-1310 du 29 octobre 2020 prescrivant les mesures générales nécessaires pour faire face à l'épidémie de Covid19 dans le cadre de l'état d'urgence sanitaire

Je soussigné{sexe},
{genre} {args.prenom} {args.nom}
Né{sexe} le {args.naissance} à {args.lieu}
Demeurant : {args.adresse} {args.ville} 
certifie que mon déplacement est lié au motif suivant autorisé par le décret n°2020-1310 du 29 octobre 2020 prescrivant les mesures générales nécessaires pour faire face à l'épidémie de Covid19 dans le cadre de l'état d'urgence sanitaire :

{motif}

Fait à {args.ville}
Le {date.day}/{date.month}/{date.year}  à {date.hour}:{date.minute}

Signature : {args.prenom} {args.nom}
'''

    file_name = os.path.join('/tmp', f'attestation-{uuid.uuid1()}.pdf')
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)
    pdf.multi_cell(180, 10, texte, 0, 'J', False)
    pdf.output(file_name, 'F')
    
    return file_name

@app.errorhandler(404)
def not_found(error):
    return {"error": "Not found"}

@api.route('/pdf')
class Todo(Resource):

    @api.doc(parser=parser)
    def get(self):
        args = parser.parse_args(strict=True)
        return send_file(document(args), as_attachment=True)

    @api.doc(parser=parser)
    def post(self):
        args = parser.parse_args(strict=True)
        return send_file(document(args), as_attachment=True)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000, debug=False)