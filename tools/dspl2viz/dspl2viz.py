import datetime
import dspl2
from flask import (
    Flask, render_template, request, Response)
from functools import lru_cache
from icu import SimpleDateFormat
from io import StringIO
import json
import os.path
import pandas as pd
from urllib.parse import urlparse


app = Flask(__name__)


@app.route('/')
def main():
    return render_template('dspl2viz.html')


@app.route('/api/measures')
def api_measures():
  dataset = request.args.get('dataset')
  if dataset is None:
    return Response("Dataset not specified", status=400)
  try:
    getter = dspl2.LocalFileGetter(
        os.path.expanduser('~/dspl/samples/bls/unemployment/bls-unemployment.jsonld'))
    expander = dspl2.Dspl2JsonLdExpander(getter)
    ds = expander.Expand(expandSlices=False)
    return Response(json.dumps(ds['measure'], indent=2), mimetype='application/json')
  except Exception as e:
    app.logger.warn(e)
    return Response("Unable to find requested dataset", status=404)


@app.route('/api/dimensions')
def api_dimensions():
  dataset = request.args.get('dataset')
  if dataset is None:
    return Response("Dataset not specified", status=400)
  try:
    getter = dspl2.HybridFileGetter(dataset)
    expander = dspl2.Dspl2JsonLdExpander(getter)
    ds = expander.Expand(expandSlices=False, expandDimensions=False)
    return Response(json.dumps(ds['dimension'], indent=2), mimetype='application/json')
  except Exception as e:
    app.logger.warn(e)
    return Response("Unable to find requested dataset", status=404)


@app.route('/api/dimension_values')
def api_dimension_values():
  dataset = request.args.get('dataset')
  if dataset is None:
    return Response("Dataset not specified", status=400)
  dimension = request.args.get('dimension')
  if dimension is None:
    return Response("Dimension not specified", status=400)
  try:
    getter = dspl2.HybridFileGetter(dataset)
    expander = dspl2.Dspl2JsonLdExpander(getter)
    ds = expander.Expand(expandSlices=False, expandDimensions=True)
    for dim in ds['dimension']:
      if (dimension == dspl2.GetUrl(dim) or
          urlparse(dimension).fragment == urlparse(dspl2.GetUrl(dim)).fragment):
        return Response(json.dumps(dim, indent=2), mimetype='application/json')
    return Response("Unable to find requested dimension", status=404)
  except Exception as e:
    app.logger.warn(e)
    return Response("Unable to find requested dataset", status=404)


@app.route('/api/slices_for_measure')
def api_slices_for_measure():
  dataset = request.args.get('dataset')
  if dataset is None:
    return Response("Dataset not specified", status=400)
  measure = request.args.get('measure')
  if measure is None:
    return Response("Measure not specified", status=400)
  try:
    getter = dspl2.HybridFileGetter(dataset)
    expander = dspl2.Dspl2JsonLdExpander(getter)
    ds = expander.Expand(expandSlices=False, expandDimensions=False)
    slices = []
    for slice in ds['slice']:
      for sliceMeasure in slice['measure']:
        if (measure == dspl2.GetUrl(sliceMeasure) or
            urlparse(measure).fragment == urlparse(dspl2.GetUrl(sliceMeasure)).fragment):
          slices.append(slice)
        break
    return Response(json.dumps(slices, indent=2),
                    mimetype='application/json')
  except Exception as e:
    app.logger.warn(e)
    return Response("Unable to find requested dataset", status=404)


@lru_cache(maxsize=10)
def _ExpandDataset(dataset):
  getter = dspl2.HybridFileGetter(dataset)
  expander = dspl2.Dspl2JsonLdExpander(getter)
  return expander.Expand()


def _ParseDate(text, date_pattern):
  df = SimpleDateFormat(date_pattern)
  ts = df.parse(text)
  return datetime.datetime.utcfromtimestamp(ts)


@lru_cache(maxsize=100)
def _GetDataSeries(dataset, slice, measure, dimension_value):
  dim_val_dict = dict([dim_val.split(':')
                       for dim_val in dimension_value.split(',')])
  ds = _ExpandDataset(dataset)
  # Identify the time dimension's date format
  dateFormat = "yyyy-MM-dd"  # default
  for dimension in ds['dimension']:
    if dimension['@type'] == 'TimeDimension':
      dateFormat = dimension.get('dateFormat')
      break

  for dsSlice in ds['slice']:
    if urlparse(dsSlice['@id']).fragment == urlparse(slice).fragment:
      ret = []
      for observation in dsSlice['data']:
        val = {}
        # Slice should have exactly the requested dims + a time dim:
        if len(observation['dimensionValues']) != len(dim_val_dict) + 1:
          continue
        # All the non-time dims should match the filter:
        matched_dims = 0
        for dim_val in observation['dimensionValues']:
          dim_id = urlparse(dim_val['dimension']).fragment
          if f'#{dim_id}' in dim_val_dict:
            if dim_val.get('codeValue') == dim_val_dict[f'#{dim_id}']:
              val[dim_id] = dim_val.get('codeValue')
              matched_dims += 1
          elif dim_val.get('value'):
            val[dim_id] = _ParseDate(dim_val.get('value'), dateFormat)
        if matched_dims != len(dim_val_dict):
          continue
        for meas_val in observation['measureValues']:
          if urlparse(meas_val['measure']).fragment == urlparse(measure).fragment:
            val[urlparse(measure).fragment] = meas_val['value']
        ret.append(val)
      return ret

@app.route('/api/series')
def api_series():
  dataset = request.args.get('dataset')
  if dataset is None:
    return Response("Dataset not specified", status=400)
  slice = request.args.get('slice')
  if slice is None:
    return Response("Slice not specified", status=400)
  measure = request.args.get('measure')
  if measure is None:
    return Response("Measure not specified", status=400)
  dimension_values = request.args.get('dimension_value')
  if dimension_values is None:
    return Response("Dimension values not specified", status=400)
  ret = _GetDataSeries(dataset, slice, measure, dimension_values)
  if ret is not None:
    out = StringIO()
    pd.DataFrame(ret).to_csv(out)
    return Response(out.getvalue(), mimetype="text/csv")
  return Response("Unable to find series for requested dimensions",
                  status=404)
