(write "Do you want to quit? [y/n] " nil)
(set answer (read))
(if (= (get answer) "y")
    (write "Goodbye!")
    (if (= (get answer) "n")
        (write "Keep on going!")
        (write (concat "Unknown answer '" answer "'"))))
