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

/**
 * @author Shardul Deo
 */
public class Value {

  private String stringValue;
  private Double floatValue;
  private Long integerValue;
  private Boolean booleanValue;
  private Long dateValue;
  private Identifier conceptValue;

  /**
   * The type of object returned by this method will be
   * {@code type.getValueType()}.
   *
   * @return Get the value for the given type
   */
  public Object getValue(DataType type) {
    switch (type) {
      case STRING:
        return stringValue;
      case FLOAT:
        return floatValue;
      case INTEGER:
        return integerValue;
      case BOOLEAN:
        return booleanValue;
      case DATE:
        return dateValue;
      case CONCEPT:
        return conceptValue;
    }
    return null;
  }

  /**
   * @return The value if it is a string
   */
  public String getStringValue() {
    return stringValue;
  }

  /**
   * Sets the string value
   */
  public void setStringValue(String stringValue) {
    this.stringValue = stringValue;
  }

  /**
   * @return The value if it is a float
   */
  public Double getFloatValue() {
    return floatValue;
  }

  /**
   * Sets the float value
   */
  public void setFloatValue(Double floatValue) {
    this.floatValue = floatValue;
  }

  /**
   * @return The value if it is an integer
   */
  public Long getIntegerValue() {
    return integerValue;
  }

  /**
   * Sets the integer value
   */
  public void setIntegerValue(Long integerValue) {
    this.integerValue = integerValue;
  }

  /**
   * @return The value if it is a boolean
   */
  public Boolean getBooleanValue() {
    return booleanValue;
  }

  /**
   * Sets the boolean value
   */
  public void setBooleanValue(Boolean booleanValue) {
    this.booleanValue = booleanValue;
  }

  /**
   * @return The value if it is a date
   */
  public Long getDateValue() {
    return dateValue;
  }

  /**
   * Sets the date value
   */
  public void setDateValue(Long dateValue) {
    this.dateValue = dateValue;
  }

  /**
   * @return The value if it is a concept
   */
  public Identifier getConceptValue() {
    return conceptValue;
  }

  /**
   * Sets the concept value
   */
  public void setConceptValue(Identifier conceptValue) {
    this.conceptValue = conceptValue;
  }
}
