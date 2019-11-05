var View;

function drawChart(event) {
  try {
    var spec = JSON.parse(event.target.value);
    spec.height = document.querySelector('#chart-container').scrollHeight;
    spec.width = document.querySelector('#chart-container').scrollWidth;
    event.target.value = JSON.stringify(spec, null, 2);
    vegaEmbed("#chart", spec)
    // result.view provides access to the Vega View API
        .then(result => {View =result})
        .catch(console.warn);
  } catch(e) {
    console.warn(e);
  }
}

var DatasetId = 'file:///usr/local/google/home/nkrishnaswami/dspl/samples/bls/unemployment/bls-unemployment.jsonld';
var SliceId = '#statesUnemploymentMonthly';
var MeasureId = '#unemployment_rate';
var DimValues = {
  seasonality: 'S',
  state: 'ST0100000000000',
};

function setSpec() {
  var vlSpec = {
    "$schema": "https://vega.github.io/schema/vega-lite/v4.0.0-beta.10.json",
    "description": "A simple bar chart with embedded data.",
    "autosize": {
      "type": "fit",
      "resize": true
    },
    "data": {
      "url": "/api/series",
      "format": {
        "type": "csv"
      }
    },
    "mark": "line",
    "encoding": {
      "x": {
        "field": "month",
        "type": "ordinal"
      },
      "y": {
        "field": "unemployment_rate",
        "type": "quantitative"
      },
      "color": {
        "field": "state",
        "type": "ordinal"
      }
    }
  }
  vlSpec.data.url += '?dataset=' + encodeURIComponent(DatasetId);
  vlSpec.data.url += '&slice=' + encodeURIComponent(SliceId);
  vlSpec.data.url += '&measure=' + encodeURIComponent(MeasureId);
  vlSpec.data.url += '&dimension_value=';
  for (var idx = 0; idx < Object.keys(DimValues).length; ++idx) {
    if (idx != 0) {
      vlSpec.data.url += ',';
    }
    var key = Object.keys(DimValues)[idx];
    var val = DimValues[key];
    vlSpec.data.url += encodeURIComponent(`#${key}:${val}`);
  }

  var input = document.querySelector("#vegalite-input");
  input.value = JSON.stringify(vlSpec, null, 2);
  input.dispatchEvent(new Event('change'));
}

function processMeasures(data) {
  let measure_container = document.querySelector('#measure-explorer');
  measure_container.innerText = "Measures:";
  console.log(measure_container);
  let ul = document.createElement('ul');
  measure_container.appendChild(ul);
  for(let measure of data) {
    let id = $('<a>', { href: measure['@id'] }).prop('hash').substring(1);
    console.log("Processing ", measure.name, 'id:', id, measure);
    let li = document.createElement('ul');
    li.innerText = measure.name;
    if (measure.description) {
      li.title = measure.description;
    }
    li.addEventListener('click', function (event) {
      for(var elt of ul.children) {
        elt.style.fontWeight = 'normal';
      }
      event.target.style.fontWeight = 'bold';
      MeasureId = '#' + id;
      setSpec();
    });
    ul.appendChild(li);
  }
}

function processSlices(data) {
  let slice_container = document.querySelector('#slice-explorer');
  slice_container.innerText = "Slices:";
  console.log(slice_container);
  let ul = document.createElement('ul');
  slice_container.appendChild(ul);
  for(let slice of data) {
    let id = $('<a>', { href: slice['@id'] }).prop('hash').substring(1);
    console.log("Processing ", slice.name, 'id:', id, slice);
    let li = document.createElement('ul');
    li.innerText = slice.name;
    if (slice.description) {
      li.title = slice.description;
    }
    li.addEventListener('click', function (event) {
      for(var elt of ul.children) {
        elt.style.fontWeight = 'normal';
      }
      event.target.style.fontWeight = 'bold';
      SliceId = '#' + id;
      setSpec();
    });
    ul.appendChild(li);
  }
}




function processDimensionValues(dimension) {
  let id = $('<a>', { href: dimension['@id'] }).prop('hash').substring(1);
  console.log("Processing ", dimension.name, 'id:', id);
  let div = document.createElement('div');
  let dimension_container = document.querySelector('#dimension-explorer');
  dimension_container.appendChild(div);
  div.innerText = dimension.name;
  if (dimension.description) {
    div.title = dimension.description;
  }
  let ul = document.createElement('ul');
  div.appendChild(ul);
  dimension.codes = {};
  for(let dimensionValue of dimension.codeList) {
    dimension.codes[dimensionValue.codeValue] = dimensionValue;
    let li = document.createElement('li');
    li.innerText = dimensionValue.name;
    if (dimensionValue.description) {
      li.title = dimensionValue.description;
    }
    li.addEventListener('click', function (event) {
      for(var elt of ul.children) {
        elt.style.fontWeight = 'normal';
      }
      event.target.style.fontWeight = 'bold';
      DimValues[id] = dimensionValue.codeValue;
      setSpec()
    });
    ul.appendChild(li);
  }
}


function processDimensions(data) {
  for(let dimension of data) {
    if (dimension.name != 'States' && dimension.name != 'Seasonality') {
      continue;
    }
    $.getJSON('/api/dimension_values?dataset=file:///usr/local/google/home/nkrishnaswami/dspl/samples/bls/unemployment/bls-unemployment.jsonld&dimension='+encodeURIComponent(dimension['@id']),
              processDimensionValues);
  }
}

document.querySelector("#vegalite-input").addEventListener('change', drawChart);
setSpec();


$.getJSON('/api/measures?dataset=' + encodeURIComponent(DatasetId), processMeasures);
// $.getJSON('/api/slices_for_measure?dataset=' + encodeURIComponent(DatasetId), processMeasures);
$.getJSON('/api/dimensions?dataset=' + encodeURIComponent(DatasetId), processDimensions);
