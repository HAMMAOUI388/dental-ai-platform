# import cv2
# from ultralytics import YOLO
# from pathlib import Path

# NUMBERING_MODEL_PATH = "../models/best.pt"

# tooth_model = YOLO(NUMBERING_MODEL_PATH)

# img_path = "p33.png"
# img = cv2.imread(img_path)

# results = tooth_model.predict(source=img_path, imgsz=2048)

# vis_img = img.copy()

# for result in results:
#     if not hasattr(result, "boxes") or len(result.boxes) == 0:
#         print("No teeth detected!")
#         continue
#     for box in result.boxes:
#         x1, y1, x2, y2 = map(int, box.xyxy[0])
#         cls = int(box.cls.item())
#         tooth_number = tooth_model.names[cls]
#         conf = float(box.conf[0])
#         print(f"Tooth {tooth_number} at ({x1},{y1},{x2},{y2}) confidence {conf:.2f}")


#         cv2.rectangle(vis_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
#         cv2.putText(vis_img, f"Tooth {tooth_number}", (x1, y1 - 5),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

# output_path = Path("numbering_result.jpg")
# cv2.imwrite(str(output_path), vis_img)
# print(f"Numbering result saved to {output_path}")

# cv2.imshow("Numbering Result", vis_img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()




from ultralytics import YOLO
# DETECTION_WEIGHTS = "/workspace/dental-ai-agent/notebooks/runs/train/dental_detectionX/weights/best.pt"
NUMBERING_WEIGHTS = "../models/best.pt"

#det_model = YOLO(DETECTION_WEIGHTS)
model = YOLO(NUMBERING_WEIGHTS)


# To test inference on a single image
results = model.predict(source="p33.png", imgsz=1024, conf=0.3)
results[0].save(save_dir="numbering_results")

