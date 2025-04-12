from fastapi import FastAPI, UploadFile, File
import cv2
import os
import numpy as np
import face_recognition
from datetime import datetime
from io import BytesIO
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change * to your frontend origin for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define path for known images and attendance log
path = 'Dataset_Images'
attendance_file = 'Attendance.csv'
images = []
classNames = []
myList = os.listdir(path)

# Load known faces
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

encodeListKnown = findEncodings(images)

# Mark attendance function
def markAttendance(name):
    with open(attendance_file, 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            dtstring = now.strftime('%Y-%m-%d %H:%M:%S')
            f.writelines(f'\n{name},{dtstring}')

# Endpoint to receive webcam images for face recognition
@app.post("/recognize_face/")
async def recognize_face(file: UploadFile = File(...)):
    contents = await file.read()
    img = np.frombuffer(contents, dtype=np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            markAttendance(name)
            return JSONResponse(content={"name": name}, status_code=200)
    
    return JSONResponse(content={"error": "No face recognized"}, status_code=400)

# Run FastAPI app with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
