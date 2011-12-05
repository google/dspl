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
 * A topic is a label that can be attached to concepts. Topics are organized
 * hierarchically.
 *
 * @author Shardul Deo
 */
public class Topic {

  private String id;
  private Info info;
  private List<Topic> childTopics;

  /**
   * @return The unique identifier of the topic in the dataset
   */
  public String getId() {
    return id;
  }

  /**
   * Sets the unique identifier of the topic in the dataset
   */
  public void setId(String id) {
    this.id = id;
  }

  /**
   * @return Textual information about the topic
   */
  public Info getInfo() {
    return info;
  }

  /**
   * Sets textual information about the topic
   */
  public void setInfo(Info info) {
    this.info = info;
  }

  /**
   * @return Topics that are children of this topic
   */
  public List<Topic> getChildTopics() {
    return childTopics;
  }

  /**
   * Sets topics that are children of this topic
   */
  public void setChildTopics(List<Topic> children) {
    this.childTopics = children;
  }

  /**
   * Adds a child topic to this topic
   */
  public void addChildTopic(Topic child) {
    if (childTopics == null) {
      childTopics = Lists.newArrayList();
    }
    childTopics.add(child);
  }
}
