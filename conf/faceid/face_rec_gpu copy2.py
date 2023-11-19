# face_rec_gpu.py
import torch
import insightface
import cv2
import numpy as np
from aiortc.contrib.media import MediaPlayer
from sklearn.metrics.pairwise import cosine_similarity

class FaceRecognition:
    def __init__(self, users, similarity, limit):
        self.users = users
        self.similarity = similarity
        self.running = True
        self.limit1 = limit
        self.limit2 = limit
        self.result1 = self.start_camera(1, "http://192.168.1.119:4747/video")
        self.result2 = None

    def camera_faces(self, model, camera, frame, faces, limit):
        while self.running and limit > 0:
            if len(faces):
                frame_embeddings = [torch.tensor(face.embedding, device='cuda') for face in faces]

                for user in self.users:
                    src_image = cv2.imread(user['path'])
                    src_faces = model.get(src_image)

                    if len(src_faces):
                        src_face = src_faces[0]
                        src_embedding = torch.tensor(src_face.embedding, device='cuda')
                    else:
                        src_embedding = None
                    if src_embedding is not None:
                        similarities = cosine_similarity(
                            [src_embedding.cpu().numpy() for _ in range(len(frame_embeddings))],
                            [fe.cpu().numpy() for fe in frame_embeddings]
                        )
                        if any(similarity > self.similarity for similarity in similarities):
                            x, y, w, h = faces[0].bbox.astype(int)
                            text_position = (x, y - 10)
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            font_scale = 0.5
                            font_color = (0, 0, 255)
                            font_thickness = 1
                            cv2.putText(frame, user['username'], text_position, font, font_scale, font_color,
                                        font_thickness)
                            cv2.imwrite("./output.jpg", frame)
                            return {"message": user, "result": True}
                limit -= 1
            else:
                limit -= 1

        return {"message": "Not known" if len(faces) else "Face not detected"}

    def start_camera(self, position, video_source):
        model = insightface.app.FaceAnalysis()
        model.prepare(ctx_id=0, det_size=(640, 640))
        cap = cv2.VideoCapture(video_source)
        _, frame = cap.read()
        faces = model.get(frame)

        if position == 1:
            return self.camera_faces(model, cap, frame, faces, self.limit1)
        else:
            return self.camera_faces(model, cap, frame, faces, self.limit2)

    def start(self, position, video_source):
        self.running = True
        result = self.result1 if position == 1 else self.result2
        return result

    def stop(self):
        self.running = False