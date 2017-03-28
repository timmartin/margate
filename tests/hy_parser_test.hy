;; Unit tests for the parser written in Hy.
;;
;; Use of Hy allows for slightly cleaner test cases when there's a lot
;; of mock object manipulation to do. In due course I'd like to see
;; all the testing done with Hy.

(import unittest
        unittest.mock
        io)

(import [stencil.compiler [Parser]]
        [stencil.code-generation [Literal Sequence IfBlock
                                  ForBlock ExtendsBlock ReplaceableBlock
                                  Execution]])

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

(defclass HyParserTest [unittest.TestCase]
  
  (defn test-extends [self]
    (setv template-locator (unittest.mock.MagicMock))
    (setv template-locator.find-template.return-value
          "/wherever/other.html")
    
    (with-mock-filesystem
      "/wherever/other.html"
      ""

      (setv parser (Parser template-locator))

      (setv sequence (parser.parse [(Execution "extends \"other.html\"")
                                    (Execution "block title")
                                    (Literal "my template")
                                    (Execution "endblock")]))
      )

    (assert-equal 1 (len sequence.elements))

    (assert-is-instance (get sequence.elements 0)
                        ExtendsBlock)

    (assert-equal [(Literal "")]
                  (. sequence elements [0] template elements))

    (assert-equal 1
                  (len (. sequence elements [0] sequence elements)))

    (assert-is-instance (. sequence elements [0] sequence elements [0])
                        ReplaceableBlock)
    
    )
  )
