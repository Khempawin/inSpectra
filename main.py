import sys
import platform
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
  return 'Hello, World!:{}.{}, {}'.format( sys.version_info[0], sys.version_info[1], platform.architecture() )

@app.route('/process/', methods=['GET','POST'])
def process():
	return 'Process'


if __name__ == '__main__':
  app.run()
