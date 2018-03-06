from flask import Flask, request
from pca import pca
from azure.storage.blob import BlockBlobService, ContentSettings
from bson import ObjectId # For ObjectId to work
from pymongo import MongoClient
import cv2
import os
import numpy as np
import pickle
import sys
import platform
import datetime
app = Flask(__name__)

#### Global parameters
DefaultAccountKey = 'VYzFODI3U3+6pXkjnCzhR+nOMaoMsF4ubrgWBdy2PEz6zYH1dA6E0qvoWgODXhXNgdxdgKZtpEOBlb0JA1HtBA=='
DefaultAccountName = 'inspectrastorage'
DefaultContainer = 'inspectracontainer'
MongoConnectionString = 'mongodb://inspectra-db:KqpVYA0yONibyKSf2wTk9hYaW4K7nyShkSe8BSU6aWrm34VA6BKOBv4gCC7Jc5KqKfQ7MdTFV91QXmczpp7dbA==@inspectra-db.documents.azure.com:10255/?ssl=true&replicaSet=globaldb'
MongoUsername = 'inspectra-db'
MongoPassword = 'KqpVYA0yONibyKSf2wTk9hYaW4K7nyShkSe8BSU6aWrm34VA6BKOBv4gCC7Jc5KqKfQ7MdTFV91QXmczpp7dbA=='
MongoDatabaseName = 'GasMonitor'
MongoCollectionName = 'pcaResults'

def getImageBlobUrl( container, blobName ):
        return 'https://inspectrastorage.blob.core.windows.net/{}/{}'.format( container, blobName )

@app.route('/')
def hello_world():
        return 'Hello, World!:{}.{}, {}'.format( sys.version_info[0], sys.version_info[1], platform.architecture() )

@app.route('/process', methods=['GET','POST'])
def processCube():
        packedData = request.data
        dataToBeProcessed = pickle.loads( packedData )

        if( not isinstance(dataToBeProcessed, dict) and not ('imageCube' in dataToBeProcessed.keys()) ):
                return 'Data dict ERROR'
        imageCube = dataToBeProcessed[ 'imageCube' ]
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
                fileTag = 'plant_{}_area{}_y{}_m{}_d{}_hr{}_min{}_sec{}'.format( dataToBeProcessed[ 'plant' ], dataToBeProcessed[ 'area' ], date.year, date.month, date.day, date.hour, date.minute, date.second )

                #	Save images to temp files
                cv2.imwrite( '_visibleTemp.PNG', visibleImage )
                cv2.imwrite( '_falseTemp.PNG', falseColorMap )

                img1=cv2.imread('_falseTemp.png',cv2.IMREAD_COLOR)
                imgList1=cv2.split(img1)
                for i in range (len(imgList1)):
                	imgList1[i]=cv2.equalizeHist(imgList1[i])
                equ=cv2.merge((imgList1[0],imgList1[1],imgList1[2]))
                cv2.imwrite('_zfalseTemp.PNG',equ)
                #       Create block blob service
                block_blob_service = BlockBlobService(account_name=DefaultAccountName, account_key=DefaultAccountKey)

                #	Save images to blob
                block_blob_service.create_blob_from_path(DefaultContainer, fileTag+'_visible', '_visibleTemp.PNG', content_settings=ContentSettings( content_type='image/png' ))                
                block_blob_service.create_blob_from_path(DefaultContainer, fileTag+'_false', '_zfalseTemp.PNG', content_settings=ContentSettings( content_type='image/png' ))
                block_blob_service.create_blob_from_path(DefaultContainer, fileTag+'_false_pca', '_falseTemp.PNG', content_settings=ContentSettings( content_type='image/png' ))

                #	Get url to images
                visibleUrl = getImageBlobUrl(DefaultContainer, fileTag+'_visible')
                falseUrl = getImageBlobUrl(DefaultContainer, fileTag+'_false')
                pcaUrl = getImageBlobUrl(DefaultContainer, fileTag+'_false_pca')

                #       delete Temp files
                #os.remove( '_visibleTemp.PNG' )
                #os.remove( '_falseTemp.PNG' )
                #os.remove( '_zfalseTemp.PNG' )
                
                #	Connect with Cosmos DB
                client = MongoClient( MongoConnectionString )
                database = client.get_database( MongoDatabaseName )
                database.authenticate( name = MongoUsername, password = MongoPassword)
                pcaResults = database.get_collection( MongoCollectionName )
                
                #	Construct Data dict to insert in Cosmos DB( MongoDB )
                recordDict = dict()
                recordDict[ 'plant' ] = dataToBeProcessed[ 'plant' ]
                recordDict[ 'area' ] = dataToBeProcessed[ 'area' ]
                recordDict[ 'timestamp' ] = date
                recordDict[ 'visible' ] = visibleUrl
                recordDict[ 'false' ] = falseUrl
                recordDict[ 'falsePca' ] = pcaUrl                
                recordDict[ 'fetchStatus' ] = False
                
                #	Insert to Cosmos DB
                pcaResults.insert( recordDict )
                
                response = pickle.dumps( recordDict )
                
                return response
        else:
                return 'Data type ERROR'


if __name__ == '__main__':
        app.run(host='0.0.0.0')
