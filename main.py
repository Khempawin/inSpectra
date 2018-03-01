from flask import Flask, request
from pca import pca
import cv2
import numpy as np
import pickle
import sys
import platform
import datetime
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

                #       Generate tag: time stamp
                date = datetime.datetime.now()
                fileTag = 'y{}_m{}_d{}_hr{}_min{}_sec{}.JPG'.format( time.year, time.month, time.day, time.hour, time.minute, time.second )

                #	Save images to temp files
                cv2.imwrite( 'visibleTemp.JPG', visibleImage )
                cv2.imwrite( 'falseTemp.JPG', falseColorMap )
                #	Save images to blob
                #	Get url to images

                #	Connect with Cosmos DB
                #	Construct Data dict to insert in Cosmos DB( MongoDB )
                #	Insert to Cosmos DB
                
                return fileTag
        else:
                return 'Data type ERROR'


if __name__ == '__main__':
        app.run(host='0.0.0.0')
