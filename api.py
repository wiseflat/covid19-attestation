#!/usr/bin/python3
import datetime
import config
import os
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from flask import Flask, jsonify, make_response, send_file, request
from flask_restplus import Resource, Api, reqparse, inputs
from flasgger import Swagger
from fpdf import FPDF

app = Flask(__name__)

def document(args, date):

  if(args.sex == 'H'):
    sex = ''
    genre = 'M.'
  else:
    sex = 'e'
    genre = 'Mme'
  if(args.reason == 'Convocation'):
    reason = "Convocation judiciaire ou administrative et pour se rendre dans un service public"
  if(args.reason == 'Missions'):
    reason = "Participation à des missions d'intérêt général sur demande de l'autorité administrative"
  if(args.reason == 'Handicap'):
    reason = "Déplacement des personnes en situation de handicap et leur accompagnant."
  if(args.reason == 'Santé'):
    reason = "Consultations, examens et soins ne pouvant être assurés à distance et l’achat de médicaments."
  if(args.reason == 'Enfants'):
    reason = "Déplacement pour chercher les enfants à l’école et à l’occasion de leurs activités périscolaires"
  if(args.reason == 'Famille'):
    reason = "Déplacements pour motif familial impérieux, pour l'assistance aux personnes vulnérables et précaires ou la garde d'enfants."
  if(args.reason == 'Sports et animaux'):
    reason = "Déplacements brefs, dans la limite d'une heure quotidienne et dans un rayon maximal d'un kilomètre autour du domicile, liés soit à l'activité physique individuelle des personnes, à l'exclusion de toute pratique sportive collective et de toute proximité avec d'autres personnes, soit à la promenade avec les seules personnes regroupées dans un même domicile, soit aux besoins des animaux de compagnie."
  if(args.reason == 'Travail'):
    reason = "Déplacements entre le domicile et le lieu d’exercice de l’activité professionnelle ou un établissement d’enseignement ou de formation, déplacements professionnels ne pouvant être différés , déplacements pour un concours ou un examen."
  if(args.reason == 'Achats'):
    reason = "Déplacements pour effectuer des achats de fournitures nécessaires à l'activité professionnelle, des achats de première nécessité3 dans des établissements dont les activités demeurent autorisées, le retrait de commande et les livraisons à domicile."

  return f'''ATTESTATION DE DÉPLACEMENT DÉROGATOIRE

En application du décret n°2020-1310 du 29 octobre 2020 prescrivant les mesures générales nécessaires pour faire face à l'épidémie de Covid19 dans le cadre de l'état d'urgence sanitaire

Je soussigné{sex},
{genre} {args.firstname} {args.lastname}
Né{sex} le {args.birthday} à {args.place_of_birth}
Demeurant : {args.address} {args.city} 
certifie que mon déplacement est lié au motif suivant autorisé par le décret n°2020-1310 du 29 octobre 2020 prescrivant les mesures générales nécessaires pour faire face à l'épidémie de Covid19 dans le cadre de l'état d'urgence sanitaire :

{reason}

Fait à {args.city}
Le {date.day}/{date.month}/{date.year}  à {date.hour}:{date.minute}

Signature : {args.firstname} {args.lastname}
'''

template = {
  "info": {
    "title": "covid API",
    "description": "API pour générer une attestation de déplacement",
    "version": "0.0.1",
    "contact": {
      "name": "Mathieu Garcia",
      "url": "https://covid19.api.wiseflat.com",
    }
  }
}

app.config['SWAGGER'] = {
    'title': 'My API',
    'uiversion': 3,
    "specs_route": "/"
}
swagger = Swagger(app, template= template)
app.config.from_object(config.Config)

api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('sex', type=inputs.regex('H|M'), required=True, help='Sexe (H/F)')
parser.add_argument('firstname', type=inputs.regex(r'^[A-Za-zàáâäçèéêëìíîïñòóôöùúûü\s]{2,20}$'), required=True, help='Prénom')
parser.add_argument('lastname', type=inputs.regex(r'^[A-Za-zàáâäçèéêëìíîïñòóôöùúûü\s-]{2,30}$'), required=True, help='Nom de famille')
parser.add_argument('birthday', type=inputs.regex(r'^([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)\d{4}$'), required=True, help='Date de naissance')
parser.add_argument('place_of_birth', type=inputs.regex(r'^[A-Za-zàáâäçèéêëìíîïñòóôöùúûü\s]{2,30}$'), required=True, help='Ville de naissance')
parser.add_argument('address', type=inputs.regex(r'^[A-Za-zàáâäçèéêëìíîïñòóôöùúûü0-9\s]{2,50}$'), required=True, help='Adresse')
parser.add_argument('city', type=inputs.regex(r'^[A-Za-zàáâäçèéêëìíîïñòóôöùúûü\s]{2,30}$'), required=True, help='Ville')
parser.add_argument('postcode', type=inputs.regex(r'\d{5}'), required=True, help='Code postal')
parser.add_argument('reason', type=inputs.regex('(Convocation|Missions|Handicap|Santé|Enfants|Famille|Sports et animaux|Travail|Achats)'), required=True, help='motif')

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not found"}), 404)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({"error": "bad request"}), 400)


@api.route('/')
class Attestation(Resource):

    def get(self):
      return jsonify(template)

    @api.doc(parser=parser)
    def post(self):
        """
        Formulaire de création de l'attestation
        ---
        parameters:
        - name: sex
          in: formData
          type: string
          required: true
          description: Sexe (H/F)
        - name: firstname
          in: formData
          type: string
          required: true
          description: Prénom
        - name: lastname
          in: formData
          type: string
          required: true
          description: Nom de famille
        - name: birthday
          in: formData
          type: string
          required: true
          description: Date de naissance
        - name: place_of_birth
          in: formData
          type: string
          required: true
          description: Ville de naissance
        - name: address
          in: formData
          type: string
          required: true
          description: Adresse
        - name: city
          in: formData
          type: string
          required: true
          description: Ville
        - name: postcode
          in: formData
          type: string
          required: true
          description: Code postal
        - name: reason
          in: formData
          type: string
          enum: ['Convocation', 'Missions', 'Handicap', 'Santé', 'Enfants', 'Famille', 'Sports et animaux', 'Travail', 'Achats']
          required: true
          description: Motif du déplacement
          default: Travail
        responses:
          500:
            description: Error
          400:
            description: Error
          200:
            description: Success
            schema:
              id: result
              properties:
                result:
                  type: boolean
                  description: Result of the request
                message:
                  type: string
                  description: A result message
        """
        args = parser.parse_args(strict=True)
        date = datetime.datetime.now()
        attestation = document(args, date)       
        file_name = os.path.join('/tmp', f'attestation-{request.remote_addr}-{date.day}{date.month}{date.year}{date.hour}{date.minute}{date.second}.pdf')
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        pdf.set_font('DejaVu', '', 12)
        pdf.multi_cell(180, 10, attestation, 0, 'J', False)
        pdf.output(file_name, 'F')
        
        return send_file(file_name, as_attachment=True)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000, debug=False)