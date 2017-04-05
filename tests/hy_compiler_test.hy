(require [tests.macros [*]])

(import unittest
        unittest.mock
        [collections [namedtuple]])

(import [stencil.compiler [Compiler]])

(defclass HyCompilerTest [unittest.TestCase]

  (defn test-compile-constant [self]
    (test-compiler "fish"
                   {}
                   "fish"))

  (defn test-compile-variable [self]
    (test-compiler "Hello {{ whom }}"
                   {:whom "world"}
                   "Hello world"))

  (defn test-compile-two-variables [self]
    (test-compiler "Hello {{ you }}, I'm {{ me }}. Nice to meet you"
                   {:you "Tim"
                    :me "an optimised template"}
                   "Hello Tim, I'm an optimised template. Nice to meet you"))

  (defn test-compile-if-block-true [self]
    (test-compiler "Conditional: {% if True %}true{% endif %}"
                   {}
                   "Conditional: true"))

  (defn test-compile-if-block-false [self]
    (test-compiler "Conditional: {% if False %}true{% endif %}"
                   {}
                   "Conditional: "))

  (defn test-compile-if-expression [self]
    (test-compiler-mult "{% if x < 10 %}x is less than 10{% endif %}"
                        [[{:x 5}
                          "x is less than 10"]

                         [{:x 20}
                          ""]]))

  (defn test-compile-for-loop [self]
    (test-compiler "Let's count: {% for i in numbers %} {{ i }} {% endfor %} done"
                   {:numbers (range 3)}
                   "Let's count:  0  1  2  done"))

  (defn test-for-if-nested [self]
    (test-compiler (+ "Odd numbers: {% for i in numbers %}{% if i % 2 %}"
                      "{{ i }} "
                      "{% endif %}{% endfor %}")
                   {:numbers (range 10)}
                   "Odd numbers: 1 3 5 7 9 "))

  (defn test-object-member [self]
    (setv Employee (namedtuple "Employee" ["name"]))
    
    (test-compiler "member: {{ employee.name }}"
                   {:employee (Employee "alice")}
                   "member: alice"))
  
  )
