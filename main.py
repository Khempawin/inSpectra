from flask import Flask, request
app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def hello_world():
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
      imageDict['rgb'] = visibleImage.mean()
      imageDict['falseColorMap'] = falseColorMap.mean()

    return 'cube received: {}'.format( imageDict )
  else:
    return 'Data type ERROR'

if __name__ == '__main__':
  app.run()
