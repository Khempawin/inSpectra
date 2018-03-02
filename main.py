from flask import Flask, request
from pca import pca
from azure.storage.blob import BlockBlobService, ContentSettings
import cv2
import os
import numpy as np
import pickle
import sys
import platform
import datetime
app = Flask(__name__)

DefaultAccountKey = 'VYzFODI3U3+6pXkjnCzhR+nOMaoMsF4ubrgWBdy2PEz6zYH1dA6E0qvoWgODXhXNgdxdgKZtpEOBlb0JA1HtBA=='
DefaultAccountName = 'inspectrastorage'
DefaultContainer = 'inspectracontainer'
DefaultImageBlob = 'spectralimageblob'
ImageBlobUrlTemplate = 'https://inspectrastorage.blob.core.windows.net/inspectracontainer/y2018_m3_d2_hr9_min51_sec29_false'

def getImageBlobUrl(container = DefaultContainer, blobName):
        pass

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
                
                #       Generate tag: time stamp
                date = datetime.datetime.now()
                fileTag = 'y{}_m{}_d{}_hr{}_min{}_sec{}'.format( date.year, date.month, date.day, date.hour, date.minute, date.second )

                #	Save images to temp files
                cv2.imwrite( 'visibleTemp.PNG', visibleImage )
                cv2.imwrite( 'falseTemp.PNG', falseColorMap )

                #       Create block blob service
                block_blob_service = BlockBlobService(account_name=DefaultAccountName, account_key=DefaultAccountKey)

                #	Save images to blob
                block_blob_service.create_blob_from_path(DefaultContainer, fileTag+'_visible', 'visibleTemp.PNG', content_settings=ContentSettings( content_type='image/png' ))                
                block_blob_service.create_blob_from_path(DefaultContainer, fileTag+'_false', 'falseTemp.PNG', content_settings=ContentSettings( content_type='image/png' ))
                #	Get url to images

                #       delete Temp files
                #os.remove( 'visible'+fileTag )
                #os.remove( 'false'+fileTag )
                
                #	Connect with Cosmos DB
                #	Construct Data dict to insert in Cosmos DB( MongoDB )
                #	Insert to Cosmos DB
                
                return fileTag
        else:
                return 'Data type ERROR'


if __name__ == '__main__':
        app.run(host='0.0.0.0')
