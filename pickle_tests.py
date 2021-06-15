import unittest
import testsMaterial
import Pickle.newPickler as pickler


def converter(obj):
    return pickler.loads(pickler.dumps(obj))


class TestSerializer(unittest.TestCase):

    def __init__(self, methodName):
        super().__init__(methodName)

    def test_empty_object(self):
        objects = testsMaterial.objects
        self.assertEqual(objects, converter(objects))

    def test_simple_string(self):
        objects = testsMaterial.string
        self.assertEqual(objects, converter(objects))

    def test_simple_obj_1(self):
        objects = testsMaterial.t1
        self.assertEqual(objects, converter(objects))

    def test_simple_obj_2(self):
        objects = testsMaterial.t2
        self.assertEqual(objects, converter(objects))

    def test_simple_obj_3(self):
        objects = testsMaterial.t3
        self.assertEqual(objects, converter(objects))

    def test_simple_func(self):
        objects = testsMaterial.simple_func
        result = converter(objects)
        self.assertEqual(objects.__code__, result.__code__)
        self.assertEqual(objects(), result())

    def test_func_with_globals_and_builtins(self):
        objects = testsMaterial.func_with_globals_and_builtins
        result = converter(objects)
        self.assertEqual(objects.__code__, result.__code__)
        self.assertEqual(objects(), result())

    def test_simple_lambda(self):
        objects = testsMaterial.simplelambda
        result = converter(objects)
        self.assertEqual(objects.__code__, result.__code__)
        self.assertEqual(objects(3), result(3))

    def test_func_with_defaults(self):
        objects = testsMaterial.func_with_defaults
        result = converter(objects)
        self.assertEqual(objects.__code__, result.__code__)
        self.assertEqual(objects(), result())

    def test_func_with_args_sum(self):
        objects = testsMaterial.func_with_args_sum
        result = converter(objects)
        self.assertEqual(objects.__code__, result.__code__)
        self.assertEqual(objects(2, 3, 4, 5), result(2, 3, 4, 5))

    def test_func_with_args_d(self):
        objects = testsMaterial.func_with_args_d
        result = converter(objects)
        self.assertEqual(objects.__code__, result.__code__)
        self.assertEqual(objects(a=4, b=3), result(a=4, b=3))

    def test_Empty_cls(self):
        objects = testsMaterial.Empty_cls
        result = converter(objects)()
        for i in objects().__dict__:
            self.assertEqual(getattr(objects(), i), getattr(result, i))

    def test_Simple_cls(self):
        objects = testsMaterial.Simple_cls
        result = converter(objects)()
        for i in objects().__dict__:
            self.assertEqual(getattr(objects(), i), getattr(result, i))

    def test_Cls_with_inheritance(self):
        objects = testsMaterial.Cls_with_inheritance
        result = converter(objects)()
        for i in objects().__dict__:
            self.assertEqual(getattr(objects(), i), getattr(result, i))

    def test_Cls_with_staticmethod(self):
        objects = testsMaterial.Cls_with_staticmethod
        result = converter(objects)()
        for i in objects().__dict__:
            self.assertEqual(getattr(objects(), i), getattr(result, i))

    def test_Inherited_cls(self):
        objects = testsMaterial.Inherited_cls
        result = converter(objects)()
        for i in objects().__dict__:
            self.assertEqual(getattr(objects(), i), getattr(result, i))

    def test_func_in_func(self):
        objects = testsMaterial.func_in_func
        result = converter(objects)
        self.assertEqual(objects.__code__, result.__code__)
        self.assertEqual(objects(2, 3, 4), result(2, 3, 4))

    def test_lambda_in_lambda(self):
        objects = testsMaterial.lambda_in_lambda
        result = converter(objects)
        self.assertEqual(objects.__code__, result.__code__)
        self.assertEqual(objects(3), converter(objects)(3))

    def test_lambda_in_function(self):
        objects = testsMaterial.lambda_in_function
        self.assertEqual(objects.__code__, converter(objects.__code__))
        self.assertEqual(objects(3), converter(objects)(3))

    def test_simplified_defaults(self):
        objects = testsMaterial.p
        result = converter(objects)
        self.assertEqual(objects.__code__, result.__code__)
        self.assertEqual(objects()(), result()())

    def test_func_wth_module(self):
        objects = testsMaterial.func_with_import_func
        result = converter(objects)
        self.assertEqual(objects.__code__, result.__code__)
        self.assertEqual(objects(2), result(2))
