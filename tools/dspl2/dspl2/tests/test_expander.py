from dspl2.expander import Dspl2JsonLdExpander, Dspl2RdfExpander
from dspl2.rdfutil import SCHEMA
from io import StringIO
import rdflib
import unittest


class DummyGetter(object):
  def __init__(self, graph):
    self.graph = graph
    self.data = {}

  def Set(self, filename, data):
    self.data[filename] = StringIO(data)

  def Fetch(self, filename):
    return self.data.get(filename, StringIO(''))


class ExpanderTests(unittest.TestCase):
  def test_Dspl2RdfExpander_ExpandDimensionValue(self):
    graph = rdflib.Graph()
    getter = DummyGetter(graph)
    expander = Dspl2RdfExpander(getter)
    dim = rdflib.URIRef('http://foo.invalid/test.json#dim')
    equiv_types = [SCHEMA.Place]
    row = {
        'codeValue': 'cv',
        'key1': 'val1',
        'key2': 'val2',
    }
    row_id = rdflib.URIRef(str(dim) + '=' + row['codeValue'])
    expander._ExpandDimensionValue(dim, equiv_types, row_id, row)
    self.assertEqual(set(graph.objects(subject=dim, predicate=SCHEMA.codeList)),
                     {row_id})
    self.assertEqual(set(graph.objects(subject=row_id,
                                       predicate=rdflib.RDF.type)),
                     {SCHEMA.DimensionValue, SCHEMA.Place})
    self.assertEqual(set(graph.objects(subject=row_id,
                                       predicate=rdflib.RDF.type)),
                     {SCHEMA.DimensionValue, SCHEMA.Place})
    self.assertEqual(set(graph.objects(subject=row_id, predicate=SCHEMA.key1)),
                     {rdflib.Literal('val1')})
    self.assertEqual(set(graph.objects(subject=row_id, predicate=SCHEMA.key2)),
                     {rdflib.Literal('val2')})
    self.assertEqual(set(graph.objects(subject=row_id,
                                       predicate=SCHEMA.codeValue)),
                     {rdflib.Literal('cv')})

  def test_Dspl2RdfExpander_ExpandFootnotes(self):
    graph = rdflib.Graph()
    dim = rdflib.URIRef('#ds')
    graph.add((dim, rdflib.RDF.type, SCHEMA.StatisticalDataset))
    graph.add((dim, SCHEMA.footnote, rdflib.Literal('foo')))
    getter = DummyGetter(graph)
    getter.Set('foo', 'codeValue,name,description\np,predicted,Value is predicted rather than measured.\n')
    expander = Dspl2RdfExpander(getter)
    expander._ExpandFootnotes()
    for triple in graph:
      print(triple)
    footnote_id = rdflib.URIRef('#footnote=p')
    self.assertEqual(set(graph.objects(subject=dim,
                                       predicate=SCHEMA.footnote)),
                     {footnote_id})
    self.assertEqual(set(graph.objects(subject=footnote_id,
                                       predicate=SCHEMA.description)),
                     {rdflib.term.Literal('Value is predicted rather than measured.')})
    self.assertEqual(set(graph.objects(subject=footnote_id,
                                       predicate=SCHEMA.name)),
                     {rdflib.term.Literal('predicted')})
    self.assertEqual(set(graph.objects(subject=footnote_id,
                                       predicate=rdflib.RDF.type)),
                     {SCHEMA.StatisticalAnnotation})
    self.assertEqual(set(graph.objects(subject=footnote_id,
                                       predicate=SCHEMA.codeValue)),
                     {rdflib.term.Literal('p')})

  def test_Dspl2RdfExpander_ExpandSliceData(self):
    pass

  def test_Dspl2JsonLdExpander_ExpandCodeList(self):
    pass

  def test_Dspl2JsonLdExpander_ExpandFootnotes(self):
    pass

  def test_Dspl2JsonLdExpander_ExpandSliceData(self):
    pass


if __name__ == '__main__':
  unittest.main()
