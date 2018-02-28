import sys
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
  return 'Hello, World!:{}'.format( sys.version_info[0] )

@app.route('/process/',methods=['GET','POST'])
def process():
	return 'Process'


if __name__ == '__main__':
  app.run()
