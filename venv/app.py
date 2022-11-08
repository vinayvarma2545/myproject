from pyexpat import model
from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine
import json
from healthcheck import HealthCheck
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics=PrometheusMetrics(app)
app.run(host="0.0.0.0" , debug=True)

health = HealthCheck()
metrics.info('app_info', 'Application info', version='1.0.3')


app.config['MONGODB_SETTINGS'] = {
  'db': 'mydb',
  'host': '127.0.0.1',
  'port': 27017
}

db = MongoEngine()
db.init_app(app)

class Workers(db.Document):
  Names = db.StringField()
  Work = db.StringField()
  WorkerId = db.IntField()
  def to_json(self):
    return {"Names": self.Names,
        "Work": self.Work,
        "WorkerId" : self.WorkerId}

@app.route("/")
def root_path():
  return("Welcome")


@app.route('/user/', methods=['GET'])
def get_user():
  labours = Workers.objects()
  if not labours:
    return jsonify({'error': 'data not found'})
  else:
    return jsonify(labours)

@app.route('/user/', methods=['POST'])
def add_user():
  record = json.loads(request.data)
  labours = Workers(Names=record['Names'],
        Work=record['Work'],
        WorkerId=record["WorkerId"])
  labours.save()
  return jsonify(labours)

@app.route('/user/<id>', methods=['PUT'])
def Update_user(id):
  record = json.loads(request.data)
  labours = Workers.objects.get_or_404(id=id)
  if not labours:
    return jsonify({'error': 'data not found'})
  else:
    labours.update(Names=record['Names'],
          Work=record['Work'],
          WorkerId=record["WorkerId"])
  return jsonify(labours)

@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):
  labours = Workers.objects(id=id)
  if not labours:
    return jsonify({'error': 'data not found'})
  else:
    labours.Workers.WorkerId.delete()
  return jsonify(labours)



class Batch(db.Document):
  Names = db.StringField()
  Course = db.StringField()
  def to_json(self):
    return {"Names": self.Names,
        "Course": self.Course,}

@app.route('/batch/', methods=['GET'])
def get_batch():
  print('1')
  batch1 = Batch.objects()
  if not batch1:
    return jsonify({'error': 'data not found'})
  else:
    return jsonify(batch1)

@app.route('/batch/', methods=['POST'])
def add_batch():
  record = json.loads(request.data)
  batch1 = Batch(Names=record['Names'],
        Course=record['Course'])
  batch1.save()
  return jsonify(batch1)



app.add_url_rule('/healthcheck', 'healthcheck', view_func=lambda: health.run())

if __name__ == "__main__":
  app.run(debug=True)
