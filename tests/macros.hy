(defmacro assert-equal [&rest args]
  `(.assertEqual self
                 ~@args))

(defmacro assert-is-instance [&rest args]
  `(.assertIsInstance self
                      ~@args))

(defmacro with-mock-filesystem [filename contents
                                &rest args]
  "Run some code in a context where the filesystem is mocked out.
  You specify the filename that will be opened during the test
  and the file contents that it should appear to have. At the end
  of the context it verifies that the file was actually opened."

  (with-gensyms [mock-file mock-obj]
    `(do (setv ~mock-file (io.StringIO ~contents))
         (setv ~mock-obj (unittest.mock.MagicMock :return-value ~mock-file))
         (with [(unittest.mock.patch "builtins.open" ~mock-obj)]
               ~@args)
         (.assert-called-once-with ~mock-obj
                                   ~filename))
    )
  )

(defmacro test-compiler [source args expectation]
  (with-gensyms [compiler function]
    `(do (setv ~compiler (Compiler))
         (setv ~function (.compile ~compiler ~source))
         (assert-equal ~expectation
                       (apply ~function [] ~args)))))

(defmacro test-compiler-mult [source cases]
  "Test compiling a single template source against a number of
  test cases."

  (with-gensyms [func compiler]
    (setv verifications
          (list-comp `(do (assert-equal ~exp
                                        (apply ~func [] ~args)))
                     [[args exp] cases]))
    `(do (setv ~compiler (Compiler))
         (setv ~func (.compile ~compiler ~source))
         ~@verifications)))
