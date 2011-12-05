// Copyright 2011, Google Inc.
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are
// met:
//
//    * Redistributions of source code must retain the above copyright
// notice, this list of conditions and the following disclaimer.
//    * Redistributions in binary form must reproduce the above
// copyright notice, this list of conditions and the following disclaimer
// in the documentation and/or other materials provided with the
// distribution.
//    * Neither the name of Google Inc. nor the names of its
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
 * The top level object that describes a dataset. This is based on the DSPL
 * schema defined at http://code.google.com/apis/publicdata/docs/schema/dspl9.html
 *
 * @author Shardul Deo
 */
public class Dataset {

  private String datasetId;
  private Info info;
  private Info provider;
  private List<Attribute> attributes;
  private List<Topic> topics;
  private List<Concept> concepts;
  private List<Slice> slices;
  private List<Table> tables;

  /**
   * @return The identifier of this dataset
   */
  public String getDatasetId() {
    return datasetId;
  }

  /**
   * Sets the identifier of this dataset
   */
  public void setDatasetId(String datasetId) {
    this.datasetId = datasetId;
  }

  /**
   * @return General information about the dataset
   */
  public Info getInfo() {
    return info;
  }

  /**
   * Sets general information about the dataset
   */
  public void setInfo(Info info) {
    this.info = info;
  }

  /**
   * @return General information about the dataset provider
   */
  public Info getProvider() {
    return provider;
  }

  /**
   * Sets general information about the dataset provider
   */
  public void setProvider(Info provider) {
    this.provider = provider;
  }

  /**
   * @return Attributes associated with this dataset
   */
  public List<Attribute> getAttributes() {
    return attributes;
  }

  /**
   * Sets attributes associated with this dataset
   */
  public void setAttributes(List<Attribute> attributes) {
    this.attributes = attributes;
  }

  /**
   * Adds an attribute to this dataset
   */
  public void addAttribute(Attribute attribute) {
    if (attributes == null) {
      attributes = Lists.newArrayList();
    }
    attributes.add(attribute);
  }

  /**
   * @return Topics defined in this dataset
   */
  public List<Topic> getTopics() {
    return topics;
  }

  /**
   * Sets topics defined in this dataset
   */
  public void setTopics(List<Topic> topics) {
    this.topics = topics;
  }

  /**
   * Adds a topic to this dataset
   */
  public void addTopic(Topic topic) {
    if (topics == null) {
      topics = Lists.newArrayList();
    }
    topics.add(topic);
  }

  /**
   * @return Concepts defined in this dataset
   */
  public List<Concept> getConcepts() {
    return concepts;
  }

  /**
   * Sets concepts defined in this dataset
   */
  public void setConcepts(List<Concept> concepts) {
    this.concepts = concepts;
  }

  /**
   * Adds a concept to this dataset
   */
  public void addConcept(Concept concept) {
    if (concepts == null) {
      concepts = Lists.newArrayList();
    }
    concepts.add(concept);
  }

  /**
   * @return Slices defined in this dataset
   */
  public List<Slice> getSlices() {
    return slices;
  }

  /**
   * Sets slices defined in this dataset
   */
  public void setSlices(List<Slice> slices) {
    this.slices = slices;
  }

  /**
   * Adds a slice to this dataset
   */
  public void addSlice(Slice slice) {
    if (slices == null) {
      slices = Lists.newArrayList();
    }
    slices.add(slice);
  }

  /**
   * @return Tables defined in this dataset
   */
  public List<Table> getTables() {
    return tables;
  }

  /**
   * Sets tables defined in this dataset
   */
  public void setTables(List<Table> tables) {
    this.tables = tables;
  }

  /**
   * Adds a table to this dataset
   */
  public void addTable(Table table) {
    if (tables == null) {
      tables = Lists.newArrayList();
    }
    tables.add(table);
  }
}
