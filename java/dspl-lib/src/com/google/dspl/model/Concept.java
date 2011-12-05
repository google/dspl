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
 * TODO: Add pluralName, totalName and synonym.
 *
 * @author Shardul Deo
 */
public class Concept {

  private String id;
  private Info info;
  private DataType type;
  private Identifier parent;
  private List<String> topics;
  private List<Attribute> attributes;
  private List<ConceptProperty> properties;
  private Value defaultValue;
  private ConceptTableMapping table;

  /**
   * @return The unique identifier of the concept in the dataset
   */
  public String getId() {
    return id;
  }

  /**
   * Sets the unique identifier of the concept in the dataset
   */
  public void setId(String id) {
    this.id = id;
  }

  /**
   * @return Textual information about the concept
   */
  public Info getInfo() {
    return info;
  }

  /**
   * Sets textual information about the concept
   */
  public void setInfo(Info info) {
    this.info = info;
  }

  /**
   * @return The data type of the concept
   */
  public DataType getType() {
    return type;
  }

  /**
   * Sets the data type of the concept
   */
  public void setType(DataType type) {
    this.type = type;
  }

  /**
   * @return The unique identifier of a concept that this concept extends
   */
  public Identifier getParent() {
    return parent;
  }

  /**
   * Sets the unique identifier of a concept that this concept extends
   */
  public void setParent(Identifier parent) {
    this.parent = parent;
  }

  /**
   * @return The topics the concept is associated with
   */
  public List<String> getTopics() {
    return topics;
  }

  /**
   * Sets the topics the concept is associated with
   */
  public void setTopics(List<String> topicIds) {
    this.topics = topicIds;
  }

  /**
   * Adds a topic the concept is associated with
   */
  public void addTopic(String topicId) {
    if (topics == null) {
      topics = Lists.newArrayList();
    }
    topics.add(topicId);
  }

  /**
   * @return The attributes of the concept
   */
  public List<Attribute> getAttributes() {
    return attributes;
  }

  /**
   * Sets the attributes of the concept
   */
  public void setAttributes(List<Attribute> attributes) {
    this.attributes = attributes;
  }

  /**
   * Adds an attribute to the concept
   */
  public void addAttribute(Attribute attribute) {
    if (attributes == null) {
      attributes = Lists.newArrayList();
    }
    attributes.add(attribute);
  }

  /**
   * @return The properties of the concept
   */
  public List<ConceptProperty> getProperties() {
    return properties;
  }

  /**
   * Sets the properties of the concept
   */
  public void setProperties(List<ConceptProperty> properties) {
    this.properties = properties;
  }

  /**
   * Adds a property to the concept
   */
  public void addProperty(ConceptProperty property) {
    if (properties == null) {
      properties = Lists.newArrayList();
    }
    properties.add(property);
  }

  /**
   * @return The default value of the concept
   */
  public Value getDefaultValue() {
    return defaultValue;
  }

  /**
   * Sets the default value of the concept
   */
  public void setDefaultValue(Value defaultValue) {
    this.defaultValue = defaultValue;
  }

  /**
   * @return The reference to a table that contains all the possible values for
   *         the concept and its non-constant properties
   */
  public ConceptTableMapping getTable() {
    return table;
  }

  /**
   * Sets the reference to a table that contains all the possible values for the
   * concept and its non-constant properties
   */
  public void setTable(ConceptTableMapping table) {
    this.table = table;
  }

  /**
   * A property of the concept. Properties represent additional information
   * about instances of the concept (e.g., a concept "city" may have a property
   * "country").
   */
  public static class ConceptProperty {

    private String id;
    private Info info;
    private DataType type;
    private Identifier concept;
    private Boolean isParent;
    private Boolean isMapping;

    /**
     * @return The identifier of the concept property
     */
    public String getId() {
      return id;
    }

    /**
     * Sets the identifier of the concept property
     */
    public void setId(String id) {
      this.id = id;
    }

    /**
     * @return Textual information about the property
     */
    public Info getInfo() {
      return info;
    }

    /**
     * Sets textual information about the property
     */
    public void setInfo(Info info) {
      this.info = info;
    }

    /**
     * @return The data type of the concept property
     */
    public DataType getType() {
      return type;
    }

    /**
     * Sets the data type of the concept property
     */
    public void setType(DataType type) {
      this.type = type;
    }

    /**
     * @return The reference to a concept that corresponds to the values of the
     *         property
     */
    public Identifier getConcept() {
      return concept;
    }

    /**
     * Sets the reference to a concept that corresponds to the values of the
     * property
     */
    public void setConcept(Identifier concept) {
      this.concept = concept;
    }

    /**
     * @return Whether this property denotes a hierarchical relationship between
     *         this concept and the referenced concept
     */
    public Boolean isParent() {
      return isParent;
    }

    /**
     * Sets whether this property denotes a hierarchical relationship between
     * this concept and the referenced concept
     */
    public void setIsParent(Boolean isParent) {
      this.isParent = isParent;
    }

    /**
     * @return Whether this property denotes a mapping (1-to-1) relationship
     *         between this concept and the referenced concept
     */
    public Boolean isMapping() {
      return isMapping;
    }

    /**
     * Sets whether this property denotes a mapping (1-to-1) relationship
     * between this concept and the referenced concept
     */
    public void setIsMapping(Boolean isMapping) {
      this.isMapping = isMapping;
    }
  }

  /**
   * A mapping to the id of the table column that contains the values of a
   * property of the concept. This mapping may be omitted if the table column
   * that contains the concept property values has the property id as its id.
   *
   * A single property can be mapped to multiple table columns (one per
   * language) by specifying different values for the language attribute.
   */
  public static class ConceptTableMapping {

    private String tableId;
    private String conceptMappingColumn;
    private List<PropertyMapping> propertyMappings;

    /**
     * @return The identifier of the table that contains data for the concept
     */
    public String getTableId() {
      return tableId;
    }

    /**
     * Sets the identifier of the table that contains data for the concept
     */
    public void setTableId(String tableId) {
      this.tableId = tableId;
    }

    /**
     * @return The identifier of the table column that contains the values of
     *         the concept
     */
    public String getConceptMappingColumn() {
      return conceptMappingColumn;
    }

    /**
     * Sets the identifier of the table column that contains the values of the
     * concept
     */
    public void setConceptMappingColumn(String conceptMappingColumn) {
      this.conceptMappingColumn = conceptMappingColumn;
    }

    /**
     * @return the mappings to the identifiers of the table columns that contain
     *         the values of the properties of the concept
     */
    public List<PropertyMapping> getPropertyMappings() {
      return propertyMappings;
    }

    /**
     * Sets the mappings to the identifiers of the table columns that contain
     * the values of the properties of the concept
     */
    public void setPropertyMappings(List<PropertyMapping> propertyMappings) {
      this.propertyMappings = propertyMappings;
    }

    /**
     * Adds a mapping to the identifier of the table column that contains the
     * values of a property of the concept
     */
    public void addPropertyMappings(PropertyMapping propertyMapping) {
      if (propertyMappings == null) {
        propertyMappings = Lists.newArrayList();
      }
      propertyMappings.add(propertyMapping);
    }
  }

  /**
   * A mapping to the identifier of the table column that contains the values of
   * a property of the concept. This mapping may be omitted if the table column
   * that contains the concept property values has the property identifier as
   * its identifier.
   *
   * A single property can be mapped to multiple table columns (one per
   * language) by specifying different values for the language attribute.
   */
  public static class PropertyMapping {

    private String propertyId;
    private String language;
    private String toColumn;

    /**
     * @return The identifier of the mapped concept property
     */
    public String getPropertyId() {
      return propertyId;
    }

    /**
     * Sets the identifier of the mapped concept property
     */
    public void setPropertyId(String propertyId) {
      this.propertyId = propertyId;
    }

    /**
     * @return The language of the values in the mapped column
     */
    public String getLanguage() {
      return language;
    }

    /**
     * Sets the language of the values in the mapped column
     */
    public void setLanguage(String language) {
      this.language = language;
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
