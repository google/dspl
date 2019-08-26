from dspl2.jsonutil import (AsList, GetSchemaProp, JsonToKwArgsDict,
                            MakeIdKeyedDict, GetSchemaId, GetSchemaType, GetUrl)
import unittest


class JsonUtilTests(unittest.TestCase):
  def test_AsList(self):
    self.assertEqual(AsList(None), [])
    self.assertEqual(AsList([]), [])
    self.assertEqual(AsList([1]), [1])
    self.assertEqual(AsList(1), [1])

  def test_GetSchemaProp(self):
    self.assertEqual(GetSchemaProp({'id': 'val'}, 'id'), 'val')
    self.assertEqual(GetSchemaProp({'schema:id': 'val'}, 'id'), 'val')

  def test_JsonToKwArgsDict(self):
    self.assertEqual(JsonToKwArgsDict({'id': 'val'}), {'dataset': {'id': 'val'}})
    self.assertEqual(JsonToKwArgsDict({}), {'dataset': {}})

  def test_MakeIdKeyedDict(self):
    objs = [{'@id': '1'}, {'@id': '2'}]
    lookup = MakeIdKeyedDict(objs)
    self.assertEqual(lookup['1'], {'@id': '1'})
    self.assertEqual(lookup['2'], {'@id': '2'})

  def test_GetSchemaId(self):
    self.assertEqual(GetSchemaId({'@id': 'val'}), 'val')
    self.assertEqual(GetSchemaId({'id': 'val'}), 'val')
    self.assertEqual(GetSchemaId({'schema:id': 'val'}), 'val')

  def test_GetSchemaType(self):
    self.assertEqual(GetSchemaType({'@type': 'val'}), 'val')
    self.assertEqual(GetSchemaType({'type': 'val'}), 'val')
    self.assertEqual(GetSchemaType({'schema:type': 'val'}), 'val')

  def test_GetUrl(self):
    self.assertEqual(GetUrl({'@id': 'val'}), 'val')
    self.assertEqual(GetUrl('val'), 'val')


if __name__ == '__main__':
    unittest.main()
