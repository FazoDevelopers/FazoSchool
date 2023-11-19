import torch
import insightface
import cv2
from imutils.video import VideoStream
from sklearn.metrics.pairwise import cosine_similarity

class FaceRecognition:
    def __init__(self, users, similarity, limit):
        self.users = users
        self.similarity = similarity
        self.running = True
        self.limit1 = limit
        self.limit2 = limit
        self.camera1_faces()

    def camera1_faces(self):
        self.model1 = insightface.app.FaceAnalysis()
        self.model1.prepare(ctx_id=0, det_size=(640, 640))
        self.camera1 = VideoStream(src="http://192.168.1.119:4747/video").start()
        self.frame1 = self.camera1.read()
        self.faces1 = self.model1.get(self.frame1)

    def camera2_faces(self):
        self.model2 = insightface.app.FaceAnalysis()
        self.model2.prepare(ctx_id=0, det_size=(640, 640))
        self.camera2 = "camera2"  # VideoStream(src="http://192.168.1.119:4747/video").start()
        self.frame2 = self.camera2.read()
        self.faces2 = self.model2.get(self.frame1)

    def start(self, position):
        self.running = True
        faces = self.faces1 if position == 1 else self.faces2
        frame = self.frame1 if position == 1 else self.frame2
        model=self.model1 if position == 1 else self.model2


        while self.running:

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
                        similarities = cosine_similarity([src_embedding.cpu().numpy() for _ in range(len(frame_embeddings))],[fe.cpu().numpy() for fe in frame_embeddings])
                        if any(similarity > self.similarity for similarity in similarities):
                            x, y, w, h = faces[0].bbox.astype(int)
                            text_position = (x, y - 10)
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            font_scale = 0.5
                            font_color = (0, 0, 255)
                            font_thickness = 1
                            cv2.putText(frame, user['username'], text_position, font, font_scale, font_color, font_thickness)
                            cv2.imwrite("./output.jpg", frame)
                            return {"message": user, "result": True}
                if self.limit1 == 0:
                    return {"message": "Not known"}
                self.limit1 -= 1
            elif self.limit2 == 0:
                return {"message": "Face not detected"}
            self.limit2 -= 1

    def stop(self):
        self.running = False
