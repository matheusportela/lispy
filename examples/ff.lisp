(defun ff (lst)
    (if (atom lst)
        lst
        (ff (car lst))))

(write (ff (list (list "a" "b") "c")))
