from dspl2.rdfutil import (LoadGraph, FrameGraph, SelectFromGraph)
from io import StringIO
import json
import rdflib
import rdflib.compare
import unittest


_SampleJson = '''{
  "@context": "http://schema.org",
  "@type": "StatisticalDataset",
  "@id": "",
  "url": "https://data.europa.eu/euodp/en/data/dataset/bAzn6fiusnRFOBwUeIo78w",
  "identifier": "met_d3dens",
  "name": "Eurostat Population Density",
  "description": "Population density by metropolitan regions",
  "dateCreated": "2015-10-16",
  "dateModified": "2019-06-18",
  "temporalCoverage": "1990-01-01/2016-01-01",
  "distribution": {
    "@type": "DataDownload",
    "contentUrl": "http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/met_d3dens.tsv.gz&unzip=true",
    "encodingFormat": "text/tab-separated-values"
  },
  "spatialCoverage":{
    "@type":"Place",
    "geo":{
      "@type":"GeoShape",
      "name": "European Union",
      "box":"34.633285 -10.468556 70.096054 34.597916"
    }
  },
  "license": "https://ec.europa.eu/eurostat/about/policies/copyright",
  "creator":{
     "@type":"Organization",
     "url": "https://ec.europa.eu/eurostat",
     "name":"Eurostat"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Eurostat",
    "url": "https://ec.europa.eu/eurostat",
    "contactPoint": {
      "@type": "ContactPoint",
      "contactType": "User Support",
      "url": "https://ec.europa.eu/eurostat/help/support"
    }
  }
}'''


class RdfUtilTests(unittest.TestCase):
  def test_LoadGraph(self):
    graph1 = LoadGraph(_SampleJson, '')
    graph2 = LoadGraph(json.loads(_SampleJson), '')
    graph3 = LoadGraph(StringIO(_SampleJson), '')
    self.assertTrue(rdflib.compare.isomorphic(graph1, graph2))
    self.assertTrue(rdflib.compare.isomorphic(graph1, graph3))

  def test_FrameGraph(self):
    json_val = FrameGraph(LoadGraph(_SampleJson, ''))
    self.assertEqual(json_val['@context'], 'http://schema.org')
    self.assertEqual(json_val['@type'], 'StatisticalDataset')
    self.assertEqual(json_val['url'], 'https://data.europa.eu/euodp/en/data/dataset/bAzn6fiusnRFOBwUeIo78w')
    self.assertEqual(json_val['identifier'], 'met_d3dens')
    self.assertEqual(json_val['name'], 'Eurostat Population Density')
    self.assertEqual(json_val['description'], 'Population density by metropolitan regions')
    self.assertEqual(json_val['dateCreated'], '2015-10-16')
    self.assertEqual(json_val['dateModified'], '2019-06-18')
    self.assertEqual(json_val['temporalCoverage'], '1990-01-01/2016-01-01')
    self.assertEqual(json_val['distribution']['@type'], 'DataDownload')
    self.assertEqual(json_val['distribution']['contentUrl'], 'http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/met_d3dens.tsv.gz&unzip=true')
    self.assertEqual(json_val['distribution']['encodingFormat'], 'text/tab-separated-values')
    self.assertEqual(json_val['spatialCoverage']['@type'], "Place")
    self.assertEqual(json_val['spatialCoverage']['geo']['@type'], "GeoShape")
    self.assertEqual(json_val['spatialCoverage']['geo']['name'], 'European Union')
    self.assertEqual(json_val['spatialCoverage']['geo']['box'], '34.633285 -10.468556 70.096054 34.597916')
    self.assertEqual(json_val['license'], 'https://ec.europa.eu/eurostat/about/policies/copyright')
    self.assertEqual(json_val['creator']['@type'], "Organization")
    self.assertEqual(json_val['creator']['url'], 'https://ec.europa.eu/eurostat')
    self.assertEqual(json_val['creator']['name'], 'Eurostat')
    self.assertEqual(json_val['publisher']['@type'], 'Organization')
    self.assertEqual(json_val['publisher']['name'], 'Eurostat')
    self.assertEqual(json_val['publisher']['url'], 'https://ec.europa.eu/eurostat')
    self.assertEqual(json_val['publisher']['contactPoint']['@type'], 'ContactPoint')
    self.assertEqual(json_val['publisher']['contactPoint']['contactType'], 'User Support')
    self.assertEqual(json_val['publisher']['contactPoint']['url'], 'https://ec.europa.eu/eurostat/help/support')

  def test_SelectFromGraph(self):
    graph = LoadGraph(_SampleJson, '')
    results = list(SelectFromGraph(
        graph,
        ('?ds', 'rdf:type', 'schema:StatisticalDataset'),
        ('?ds', 'schema:name', '?name')))
    self.assertEqual(len(results), 1)
    self.assertEqual(results[0]['name'], 'Eurostat Population Density')


if __name__ == '__main__':
    unittest.main()
