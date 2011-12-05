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

import com.google.common.collect.Maps;

import java.util.Locale;
import java.util.Map;

/**
 * Textual information about an element of the dataset.
 *
 * @author Shardul Deo
 */
public class Info {

  private Map<String, String> names;
  private Map<String, String> descriptions;
  private Map<String, String> urls;

  /**
   * @return Name for the given locale
   */
  public String getName(Locale locale) {
    return names.get(locale.toString());
  }

  /**
   * Sets name for the given locale
   */
  public void setName(Locale locale, String name) {
    if (names == null) {
      names = Maps.newHashMap();
    }
    names.put(locale.toString(), name);
  }

  /**
   * @return Map of language to localized names
   */
  public Map<String, String> getNames() {
    return names;
  }

  /**
   * Sets map of language to localized names
   */
  public void setNames(Map<String, String> names) {
    this.names = names;
  }

  /**
   * @return Description for the given locale
   */
  public String getDescription(Locale locale) {
    return descriptions.get(locale.toString());
  }

  /**
   * Sets description for the given locale
   */
  public void setDescription(Locale locale, String description) {
    if (descriptions == null) {
      descriptions = Maps.newHashMap();
    }
    descriptions.put(locale.toString(), description);
  }

  /**
   * @return Map of language to localized descriptions
   */
  public Map<String, String> getDescriptions() {
    return descriptions;
  }

  /**
   * Sets map of language to localized descriptions
   */
  public void setDescriptions(Map<String, String> descriptions) {
    this.descriptions = descriptions;
  }

  /**
   * @return Url for the given locale
   */
  public String getUrl(Locale locale) {
    return urls.get(locale.toString());
  }

  /**
   * Sets url for the given locale
   */
  public void setUrl(Locale locale, String url) {
    if (urls == null) {
      urls = Maps.newHashMap();
    }
    urls.put(locale.toString(), url);
  }

  /**
   * @return Map of language to localized urls
   */
  public Map<String, String> getUrls() {
    return urls;
  }

  /**
   * Sets map of language to localized urls
   */
  public void setUrls(Map<String, String> urls) {
    this.urls = urls;
  }
}
