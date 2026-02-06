import cv2

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_skin = (0, 20, 70)
    upper_skin = (20, 255, 255)

    mask = cv2.inRange(hsv, lower_skin, upper_skin)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    mask = cv2.erode(mask, kernel, 2)
    mask = cv2.dilate(mask, kernel, 2)

    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    hand_count = 0

    for cnt in contours:
        area = cv2.contourArea(cnt)

        # 🔑 Area threshold (tune this)
        if area > 5000:
            hand_count += 1
            cv2.drawContours(frame, [cnt], -1, (0,255,0), 2)

    cv2.putText(
        frame,
        f"Hands detected: {hand_count}",
        (20,40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,0,255),
        2
    )

    cv2.imshow("Multiple Hand Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
