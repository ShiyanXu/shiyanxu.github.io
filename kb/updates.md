---
layout: kb
title: 更新日志
kb_home: false
---

# 更新日志

这个知识库按天记录增删改。每天 22:30 自动扫描一次源目录，有改动才提交一版，没改动就什么都不做。

{% assign wd = "周一,周二,周三,周四,周五,周六,周日" | split: "," %}
<div class="kb-stats">
  <div class="kb-stat"><b>{{ site.data.kb_updates.days | size }}</b><span>天有更新</span></div>
  <div class="kb-stat"><b>{{ site.data.kb.total }}</b><span>篇笔记</span></div>
  <div class="kb-stat"><b>{{ site.data.kb.categories | size }}</b><span>个分类</span></div>
</div>

<div class="kb-days">
{% for day in site.data.kb_updates.days %}
  {% assign wd_idx = day.date | date: "%u" | minus: 1 %}
  <section class="kb-day">
    <div class="kb-day-head">
      <span class="kb-day-date">{{ day.date | date: "%Y-%m-%d" }}</span>
      <span class="kb-day-week">{{ wd[wd_idx] }}</span>
      <span class="kb-day-sum">
        {% if day.added.size > 0 %}新增 {{ day.added.size }}{% endif %}
        {% if day.modified.size > 0 %}{% if day.added.size > 0 %} · {% endif %}修改 {{ day.modified.size }}{% endif %}
        {% if day.removed.size > 0 %}{% if day.added.size > 0 or day.modified.size > 0 %} · {% endif %}移除 {{ day.removed.size }}{% endif %}
      </span>
    </div>

    {% for item in day.added %}
    <div class="kb-upd">
      <span class="kb-upd-tag">新增</span>
      <a href="{{ item.url | relative_url }}">{{ item.title }}</a>
      <span class="kb-upd-cat">{{ item.category }}</span>
    </div>
    {% endfor %}

    {% for item in day.modified %}
    <div class="kb-upd">
      <span class="kb-upd-tag mod">修改</span>
      <a href="{{ item.url | relative_url }}">{{ item.title }}</a>
      <span class="kb-upd-cat">{{ item.category }}</span>
    </div>
    {% endfor %}

    {% for item in day.removed %}
    <div class="kb-upd">
      <span class="kb-upd-tag del">移除</span>
      <span>{{ item.title }}</span>
      <span class="kb-upd-cat">{{ item.category }}</span>
    </div>
    {% endfor %}
  </section>
{% else %}
  <p>还没有记录。第一次同步后，这里会按天列出知识库的变化。</p>
{% endfor %}
</div>
