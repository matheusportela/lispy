(defun area (r)
    (let ((pi 3.1415926535))
        (* pi (pow r 2))))

(defun perimeter (r)
    (let ((pi 3.1415926535))
        (* 2 pi r)))

(write "CIRCLE CALCULATOR")
(write "Circle radius: " nil)
(set r (float (read)))
(write (concat "Perimeter: " (str (perimeter (get r)))))
(write (concat "Area: " (str (area (get r)))))

