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

import com.google.common.collect.Maps;

import java.util.Locale;
import java.util.Map;

/**
 * An attribute of a dataset or a concept.
 *
 * @author Shardul Deo
 */
public class Attribute {

  private String id;
  private Info info;
  private DataType type;
  private Value value;
  private Map<String, String> stringValues;

  /**
   * @return The identifier of the attribute
   */
  public String getId() {
    return id;
  }

  /**
   * Sets the identifier of the attribute
   */
  public void setId(String id) {
    this.id = id;
  }

  /**
   * @return Textual information about the attribute
   */
  public Info getInfo() {
    return info;
  }

  /**
   * Sets textual information about the attribute
   */
  public void setInfo(Info info) {
    this.info = info;
  }

  /**
   * @return The data type of the attribute
   */
  public DataType getType() {
    return type;
  }

  /**
   * Sets the data type of the attribute
   */
  public void setType(DataType type) {
    this.type = type;
  }

  /**
   * @return Value of the attribute if it is not a multi-locale value
   */
  public Value getValue() {
    return value;
  }

  /**
   * Sets value of the attribute
   */
  public void setValue(Value value) {
    this.value = value;
  }

  /**
   * @return Value of the attribute for the given locale if it is a multi-locale
   *         string value
   */
  public String getValue(Locale locale) {
    return stringValues.get(locale.toString());
  }

  /**
   * Sets the value of the attribute for the given locale
   */
  public void setValue(Locale locale, String value) {
    if (stringValues == null) {
      stringValues = Maps.newHashMap();
    }
    stringValues.put(locale.toString(), value);
  }

  /**
   * @return Map of language to localized string values of the attribute if it
   *         is a multi-locale string value
   */
  public Map<String, String> getStringValues() {
    return stringValues;
  }

  /**
   * Sets map of language to localized string values of the attribute
   */
  public void setStringValues(Map<String, String> stringValues) {
    this.stringValues = stringValues;
  }
}
