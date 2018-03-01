from flask import Flask, request
from pca import pca
import cv2
import numpy as np
import pickle
import sys
import platform
app = Flask(__name__)

@app.route('/')
def hello_world():
  return 'Hello, World!:{}.{}, {}'.format( sys.version_info[0], sys.version_info[1], platform.architecture() )

@app.route('/process', methods=['GET','POST'])
def processCube():
    packedData = request.data
    imageCube = pickle.loads( packedData )
    if( isinstance(imageCube, np.ndarray) ):
      # Keep image dimensions
      bands, row, column = imageCube.shape
      # tranform image cube to image matrix
      imageMatrix = []
      for i in range(bands):
        imageMatrix.append(imageCube[i].flatten())

      imageMatrix = np.array( imageMatrix )

      # perform pca
      eigenVector, pcList = pca( imageMatrix, row, column )

      # Pack data for response
      visibleImage = cv2.merge((imageCube[0],imageCube[1],imageCube[2]))
      falseColorMap = cv2.merge((pcList[0],pcList[1],pcList[2]))

      imageDict = dict()
      imageDict['rgb'] = visibleImage
      imageDict['falseColorMap'] = falseColorMap

      imageDictPack = pickle.dumps( imageDict )
      return imageDictPack
      #mean = unpackedData.mean()
      #return 'cube received: {}'.format( mean )
    else:
      return 'Data type ERROR'


if __name__ == '__main__':
  app.run(host='0.0.0.0')
