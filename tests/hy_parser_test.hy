;; Unit tests for the parser written in Hy.
;;
;; Use of Hy allows for slightly cleaner test cases when there's a lot
;; of mock object manipulation to do. In due course I'd like to see
;; all the testing done with Hy.

(require [tests.macros [*]])

(import unittest
        unittest.mock
        io)

(import [margate.parser [Parser]]
        [margate.code-generation [Literal Sequence IfBlock
                                  ForBlock ExtendsBlock ReplaceableBlock
                                  Execution]])

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
