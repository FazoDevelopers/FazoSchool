# face_id_gpu.py
import torch
import insightface
import cv2
from imutils.video import VideoStream
from sklearn.metrics.pairwise import cosine_similarity

class FaceRecognition:
    def __init__(self, users, similarity, limit):
        self.model = insightface.app.FaceAnalysis(providers=['CUDAExecutionProvider','CPUExecutionProvider'])
        self.users = users
        self.similarity = similarity
        self.running = True
        self.limit1 = limit
        self.limit2 = limit
        self.camera1 = VideoStream(src="http://192.168.1.119:4747/video").start()
        self.camera2 = "camera2"  # VideoStream(src="http://192.168.1.119:4747/video").start()
        self.model.prepare(ctx_id=0, det_size=(640, 640))
        self.vs = None

    def start(self, position, video_source):
        self.running = True
        self.vs = self.camera1 if position == 1 else self.camera2
        frame = self.vs.read()
        self.faces = self.model.get(frame)

        while self.running:
            if self.faces:
                for face in self.faces:
                    frame_embedding = torch.tensor(face.embedding, device='cuda')
                    x, y, w, h = face.bbox.astype(int)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    for user in self.users:
                        src_image = cv2.imread(user['path'])
                        src_faces = self.model.get(src_image)

                        if src_faces:
                            src_face = src_faces[0]
                            src_embedding = torch.tensor(src_face.embedding, device='cuda')
                        else:
                            src_embedding = None

                        if src_embedding is not None:
                            similarity = cosine_similarity(
                                [src_embedding.cpu().numpy()],
                                [frame_embedding.cpu().numpy()]
                            )[0][0]

                            if similarity > self.similarity:
                                text_position = (x, y - 10)
                                font = cv2.FONT_HERSHEY_SIMPLEX
                                font_scale = 0.5
                                font_color = (0, 0, 255)
                                font_thickness = 1
                                cv2.putText(frame, user['username'], text_position, font, font_scale, font_color,
                                            font_thickness)
                                cv2.imwrite("./output.jpg", frame)
                                return {"message": user, "result": True}

                            if user == self.users[-1] and self.limit1 == 0:
                                return {"message": "Not known"}

                            self.limit1 -= 1

                        else:
                            return {"message": "src_embedding is None"}

            elif not self.faces and self.limit2 == 0:
                return {"message": "face hasn't"}

            self.limit2 -= 1

    def stop(self):
        self.running = False
