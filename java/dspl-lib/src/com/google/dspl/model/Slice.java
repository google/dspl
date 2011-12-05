// Copyright 2011, Google Inc.
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are
// met:
//
// * Redistributions of source code must retain the above copyright
// notice, this list of conditions and the following disclaimer.
// * Redistributions in binary form must reproduce the above
// copyright notice, this list of conditions and the following disclaimer
// in the documentation and/or other materials provided with the
// distribution.
// * Neither the name of Google Inc. nor the names of its
// contributors may be used to endorse or promote products derived from
// this software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
// "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
// LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
// A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
// OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
// LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
// DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
// THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

package com.google.dspl.model;

import com.google.common.collect.Lists;

import java.util.List;

/**
 * A slice describes a combination of concepts for which data exists. Metrics
 * are the concepts that provide values, while dimensions are the concepts used
 * to access these values. More precisely, the dimensions are a primary key for
 * the data of the slice. That is, for any combination of values of the
 * dimensions, there is at most one data row in the slice.
 *
 * @author Shardul Deo
 */
public class Slice {

  private String id;
  private Info info;
  private List<Identifier> dimensions;
  private List<Identifier> metrics;
  private TableMapping table;

  /**
   * @return The unique identifier of the slice in the dataset
   */
  public String getId() {
    return id;
  }

  /**
   * Sets the unique identifier of the slice in the dataset
   */
  public void setId(String id) {
    this.id = id;
  }

  /**
   * @return Textual information about the slice
   */
  public Info getInfo() {
    return info;
  }

  /**
   * Sets textual information about the slice
   */
  public void setInfo(Info info) {
    this.info = info;
  }

  /**
   * @return Dimensions in the slice
   */
  public List<Identifier> getDimensions() {
    return dimensions;
  }

  /**
   * Sets dimensions for the slice
   */
  public void setDimensions(List<Identifier> dimensions) {
    this.dimensions = dimensions;
  }

  /**
   * Adds a dimension to the slice
   */
  public void addDimension(Identifier dimension) {
    if (dimensions == null) {
      dimensions = Lists.newArrayList();
    }
    dimensions.add(dimension);
  }

  /**
   * @return Metrics in the slice
   */
  public List<Identifier> getMetrics() {
    return metrics;
  }

  /**
   * Sets metrics for the slice
   */
  public void setMetrics(List<Identifier> metrics) {
    this.metrics = metrics;
  }

  /**
   * Adds a metric to the slice
   */
  public void addMetric(Identifier metric) {
    if (metrics == null) {
      metrics = Lists.newArrayList();
    }
    metrics.add(metric);
  }

  /**
   * @return Mapping to a table where the slice data can be accessed
   */
  public TableMapping getTable() {
    return table;
  }

  /**
   * Sets mapping to a table where the slice data can be accessed
   */
  public void setTable(TableMapping table) {
    this.table = table;
  }

  /**
   * A mapping to a table that provides data for a slice.
   */
  public static class TableMapping {

    private String tableId;
    private List<ConceptMapping> dimensionMappings;
    private List<ConceptMapping> metricMappings;

    /**
     * @return The identifier of the table that contains data for the slice
     */
    public String getTableId() {
      return tableId;
    }

    /**
     * Sets the identifier of the table that contains data for the slice
     */
    public void setTableId(String tableId) {
      this.tableId = tableId;
    }

    /**
     * @return Mappings to the table columns that contain values for the
     *         dimensions of the slice
     */
    public List<ConceptMapping> getDimensionMappings() {
      return dimensionMappings;
    }

    /**
     * Sets mappings to the table columns that contain values for the dimensions
     * of the slice
     */
    public void setDimensionMappings(List<ConceptMapping> dimensionMappings) {
      this.dimensionMappings = dimensionMappings;
    }

    /**
     * Adds mapping to a table column that contains values for a dimension of
     * the slice
     */
    public void addDimensionMapping(ConceptMapping dimensionMapping) {
      if (dimensionMappings == null) {
        dimensionMappings = Lists.newArrayList();
      }
      dimensionMappings.add(dimensionMapping);
    }

    /**
     * @return Mappings to the table columns that contain values for the metrics
     *         of the slice
     */
    public List<ConceptMapping> getMetricMappings() {
      return metricMappings;
    }

    /**
     * Sets mappings to the table columns that contain values for the metrics of
     * the slice
     */
    public void setMetricMappings(List<ConceptMapping> metricMappings) {
      this.metricMappings = metricMappings;
    }

    /**
     * Adds mapping to a table column that contains values for a metric of the
     * slice
     */
    public void addMetricMapping(ConceptMapping metricMapping) {
      if (metricMappings == null) {
        metricMappings = Lists.newArrayList();
      }
      metricMappings.add(metricMapping);
    }
  }

  /**
   * A mapping to the id of the table column that contains the values of a
   * dimension or metric of the slice. This mapping may be omitted if the table
   * column that contains the slice dimension/metric values has the concept id
   * as its column id. If the referenced concept comes from an external dataset,
   * the mapping may be omitted if the id of the column matches the local id of
   * the concept.
   */
  public static class ConceptMapping {

    private Identifier concept;
    private String toColumn;

    /**
     * @return The identifier of the mapped dimension/metric concept
     */
    public Identifier getConcept() {
      return concept;
    }

    /**
     * Sets the identifier of the mapped dimension/metric concept
     */
    public void setConcept(Identifier concept) {
      this.concept = concept;
    }

    /**
     * @return The identifier of the mapped table column
     */
    public String getToColumn() {
      return toColumn;
    }

    /**
     * Sets the identifier of the mapped table column
     */
    public void setToColumn(String toColumn) {
      this.toColumn = toColumn;
    }
  }
}
